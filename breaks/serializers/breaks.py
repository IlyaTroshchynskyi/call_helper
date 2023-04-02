import datetime

# from crum import get_current_user
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from breaks.constants import REPLACEMENT_MEMBER_BREAK, REPLACEMENT_MEMBER_OFFLINE, REPLACEMENT_MEMBER_ONLINE
from breaks.models.organisations import Break, Replacement, ReplacementMember, GroupInfo
from common.serializers import InfoModelSerializer, ExtendedModelSerializer, DictMixinSerializer
from common.validators import Time15MinutesValidator

from common.services import convert_timedelta_to_str_time

User = get_user_model()


class BreakSettingsSerializer(ExtendedModelSerializer):
    class Meta:
        model = GroupInfo
        exclude = ("group",)


class ReplacementShortSerializer(InfoModelSerializer):
    class Meta:
        model = Replacement
        fields = ("id", "date", "break_start", "break_end", "break_max_duration", "min_active")


class ReplacementMemberShortSerializer(ExtendedModelSerializer):
    id = serializers.CharField(source="member.employee.user.pk")
    full_name = serializers.CharField(source="member.employee.user.full_name")
    username = serializers.CharField(source="member.employee.user.username")
    email = serializers.CharField(source="member.employee.user.email")
    description = serializers.SerializerMethodField()
    status = DictMixinSerializer()

    class Meta:
        model = ReplacementMember
        fields = ("id", "full_name", "username", "email", "status", "description")

    def get_description(self, instance):
        if not instance.break_start:
            return None

        now = datetime.datetime.now().astimezone()
        break_start = datetime.datetime.combine(now.date(), instance.break_start).astimezone()
        break_end = datetime.datetime.combine(now.date(), instance.break_end).astimezone()

        if break_start > now:
            delta = break_start - now
            return f"Lunch starts in {convert_timedelta_to_str_time(delta)}"
        elif break_end > now:
            delta = break_end - now
            return f"Lunch ends in {convert_timedelta_to_str_time(delta)}"

        return None


class BreakMeRetrieveSerializer(InfoModelSerializer):
    replacement = ReplacementShortSerializer()

    class Meta:
        model = Break
        fields = ("id", "replacement", "break_start", "break_end")


class BreakMeUpdateSerializer(InfoModelSerializer):
    status = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Break
        fields = ("id", "break_start", "break_end", "status")
        extra_kwargs = {
            "break_start": {"validators": [Time15MinutesValidator()]},
            "break_end": {"validators": [Time15MinutesValidator()]},
        }

    def validate(self, attrs):
        try:
            instance_id = self.instance.pk
        except:
            instance_id = None

        replacement = self.get_object_from_url(Replacement)
        user = self.context["request"].user

        member = ReplacementMember.objects.filter(replacement=replacement, member__employee__user=user).first()

        now = timezone.now().date()
        if replacement.date != now:
            raise ParseError("The break reservation time has already expired or has not started yet.")
        if not member:
            raise ParseError("You do not have access to the current shift.")

        if "break_start" in attrs and "break_end" in attrs:
            if attrs["break_start"] < replacement.break_start:
                raise ParseError("The start time must not be less than the time specified in the shift.")
            if attrs["break_end"] > replacement.break_end:
                raise ParseError("End time should not be more than the time specified in the shift")
            if attrs["break_start"] >= attrs["break_end"]:
                raise ParseError("The start time must not be greater than the end time")

            max_duration = datetime.timedelta(minutes=replacement.break_max_duration)
            break_start = datetime.datetime.combine(datetime.date.today(), attrs["break_start"])
            break_end = datetime.datetime.combine(datetime.date.today(), attrs["break_end"])
            if break_start + max_duration < break_end:
                raise ParseError("Lunch duration exceeds the maximum set value.")

            free_breaks = replacement.free_breaks_available(attrs["break_start"], attrs["break_end"], instance_id)
            if free_breaks <= replacement.min_active:
                raise ParseError("There are no available seats for the selected interval.")
            attrs["replacement"] = replacement
            attrs["member"] = member

            if not instance_id:
                if replacement.breaks.filter(member=member).exists():
                    raise ParseError("You have already booked your lunch break.")

        return attrs

    def validate_status(self, value):
        if value not in ["break_start", "break_end"]:
            raise ParseError("Status should be break_start or break_end")

        if self.instance.member.status_id == REPLACEMENT_MEMBER_OFFLINE:
            raise ParseError("Unable to start lunch while your status is Offline.")

        if value == "break_start":
            now = datetime.datetime.now().astimezone()
            break_start = datetime.datetime.combine(
                self.instance.replacement.date, self.instance.break_start
            ).astimezone()
            if now + datetime.timedelta(minutes=5) < break_start:
                raise ParseError("Lunch time hasn't started yet.")
            if self.instance.member.time_break_start:
                raise ParseError("The lunch break has already begun.")
        else:
            if not self.instance.member.time_break_start:
                raise ParseError("Lunch break hasn't started yet.")
            if self.instance.member.time_break_end:
                raise ParseError("The lunch break is already over.")
        return value

    def update(self, instance, validated_data):
        status = validated_data.pop("status", None)
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if status:
                member = instance.member
                if status == "break_start":
                    member.status_id = REPLACEMENT_MEMBER_BREAK
                elif status == "break_end":
                    member.status_id = REPLACEMENT_MEMBER_ONLINE
                member.save()
        return instance


class BreakScheduleSerializer(serializers.Serializer):
    final_line = serializers.SerializerMethodField()

    def get_final_line(self, instance):
        line = [self.get_instance(instance)]
        pre_blank = self.get_pre_blank(instance)
        if pre_blank["colspan"] > 0:
            line.append(pre_blank)
        line.append(self.get_break(instance))
        post_blank = self.get_post_blank(instance)
        if post_blank["colspan"] > 0:
            line.append(post_blank)
        return line

    def get_instance(self, instance):
        result = self._convert_to_cell(value=instance.member.member.employee.user.full_name, ncolor="#fff", span=2)
        return result

    def get_pre_blank(self, instance):
        span = self._get_span_count(instance.replacement.break_start, instance.break_start)
        return self._convert_to_cell(span=span)

    def get_break(self, instance):
        span = self._get_span_count(instance.break_start, instance.break_end)
        break_start = instance.break_start.strftime("%H:%M")
        break_end = instance.break_end.strftime("%H:%M")
        value = f"{break_start} - {break_end}"
        color = instance.member.status.color
        return self._convert_to_cell(value, color, span)

    def get_post_blank(self, instance):
        span = self._get_span_count(instance.break_end, instance.replacement.break_end)
        return self._convert_to_cell(span=span)

    def _convert_to_cell(self, value="", color="#fff", span=None):
        obj = {"value": value, "color": color}
        if span is not None:
            obj["colspan"] = span
        return obj

    def _get_span_count(self, start_board, start_instance):
        board_minutes = start_board.hour * 60 + start_board.minute
        instance_minutes = start_instance.hour * 60 + start_instance.minute
        span = int((instance_minutes - board_minutes) / 15)
        return span

    def to_representation(self, instance):
        return self.fields["final_line"].to_representation(instance)

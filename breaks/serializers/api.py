import datetime
from time import timezone

from django.db import transaction
from django.db.models import Count, Q
from rest_framework import serializers
from rest_framework.exceptions import ParseError
from rest_framework.fields import SerializerMethodField, BooleanField
from rest_framework.relations import PrimaryKeyRelatedField

from breaks.constants import (
    REPLACEMENT_MEMBER_ONLINE,
    REPLACEMENT_MEMBER_OFFLINE,
    REPLACEMENT_MEMBER_BUSY,
    REPLACEMENT_MEMBER_BREAK,
)
from breaks.serializers.breaks import ReplacementMemberShortSerializer
from common.serializers import ExtendedModelSerializer, StatusMixinSerializer, InfoModelSerializer, DictMixinSerializer
from breaks.models.organisations import (
    ReplacementStatus,
    ReplacementEmployee,
    BreakStatus,
    GroupInfo,
    Replacement,
    Break,
    ReplacementMember,
)
from common.services import convert_timedelta_to_str_time
from organisations.models import Group, Member
from organisations.serializers.nested.groups import GroupShortSerializer


class BreakForReplacementSerializer(ExtendedModelSerializer):
    class Meta:
        model = Break
        fields = ("id", "break_start", "break_end")
        extra_kwargs = {
            "break_start": {"format": "%H:%M"},
            "break_end": {"format": "%H:%M"},
        }


class ReplacementGeneralSerializer(ExtendedModelSerializer):
    group = GroupShortSerializer(source="group.group")
    break_start = serializers.TimeField(format="%H:%M")
    break_end = serializers.TimeField(format="%H:%M")
    date = serializers.DateField(format="%d.%m.%Y")

    class Meta:
        model = Replacement
        fields = ("id", "group", "date", "break_start", "break_end", "break_max_duration", "min_active")


class ReplacementPersonalStatsSerializer(ExtendedModelSerializer):
    time_online = serializers.DateTimeField(format="%H:%M")
    time_break_start = serializers.DateTimeField(format="%H:%M")
    time_break_end = serializers.DateTimeField(format="%H:%M")
    time_offline = serializers.DateTimeField(format="%H:%M")
    time_until_break = serializers.SerializerMethodField()

    class Meta:
        model = ReplacementMember
        fields = ("time_online", "time_break_start", "time_break_end", "time_offline", "time_until_break")

    @property
    def data(self):
        data = super().data
        if "time_until_break" not in data:
            data["time_until_break"] = None
        return data

    def get_time_until_break(self, instance):
        if not instance:
            return None
        break_obj = instance.breaks.filter(replacement=instance.replacement).first()
        if not break_obj:
            return None

        now = datetime.datetime.now().time()
        now_minutes = now.hour * 60 + now.minute
        break_minutes = break_obj.break_start.hour * 60 + break_obj.break_start.minute

        delta = break_minutes - now_minutes

        if delta < 0:
            return None

        delta_hours = delta // 60
        delta_minutes = delta % 60
        result = f"{delta_hours // 10}{delta_hours % 10}:{delta_minutes // 10}{delta_minutes % 10}"
        return result


class ReplacementBreakSerializer(serializers.Serializer):
    info = serializers.SerializerMethodField()
    button = serializers.SerializerMethodField()

    def get_info(self, instance):
        user = self.context["request"].user
        break_obj = instance.get_break_for_user(user)
        return BreakForReplacementSerializer(break_obj, allow_null=True).data

    def get_button(self, instance):
        user = self.context["request"].user
        return instance.get_break_status_for_user(user)


class ReplacementActionSerializer(serializers.Serializer):
    replacement_button = serializers.SerializerMethodField()
    break_button = serializers.SerializerMethodField()

    def get_replacement_button(self, instance):
        now = timezone.now().astimezone()
        if instance.date != now.date():
            return None
        user = self.context["request"].user
        member = instance.get_member_by_user(user)
        if not member:
            return None

    def get_button(self, instance):
        user = self.context["request"].user
        return instance.get_break_status_for_user(user)


class ReplacementListSerializer(InfoModelSerializer):
    group = GroupShortSerializer(source="group.group")

    class Meta:
        model = Replacement
        fields = ("id", "group", "date", "break_start", "break_end", "break_max_duration", "min_active")


class ReplacementRetrieveSerializer(InfoModelSerializer):
    stats = SerializerMethodField()
    general = ReplacementGeneralSerializer(source="*")
    personal_stats = SerializerMethodField()
    breaks = ReplacementBreakSerializer(source="*")
    actions = SerializerMethodField()
    members = ReplacementMemberShortSerializer(source="members_info", many=True)

    class Meta:
        model = Replacement
        fields = (
            "id",
            "group",
            "date",
            "break_start",
            "break_end",
            "break_max_duration",
            "min_active",
            "stats",
            "personal_stats",
            "breaks",
            "actions",
            "members",
            "general",
        )

    def get_personal_stats(self, instance):
        user = self.context["request"].user
        member = instance.get_member_by_user(user)
        return ReplacementPersonalStatsSerializer(member, allow_null=True).data

    def get_stats(self, instance):
        result = self.Meta.model.objects.filter(pk=instance.pk).aggregate(
            members_count=Count("members", distinct=True),
            breaks_count=Count("breaks", distinct=True),
            members_online=Count("members", filter=Q(members_info__status_id=REPLACEMENT_MEMBER_ONLINE), distinct=True),
            members_offline=Count(
                "members", filter=Q(members_info__status_id=REPLACEMENT_MEMBER_OFFLINE), distinct=True
            ),
            members_busy=Count("members", filter=Q(members_info__status_id=REPLACEMENT_MEMBER_BUSY), distinct=True),
            members_break=Count("members", filter=Q(members_info__status_id=REPLACEMENT_MEMBER_BREAK), distinct=True),
        )
        return result

    def get_actions(self, instance):
        result = {
            "replacement_button": None,
            "break_button": None,
        }
        now = datetime.datetime.now().astimezone()
        if instance.date != now.date():
            return result
        user = self.context["request"].user
        member = instance.get_member_by_user(user)
        if not member:
            return result

        # replacement_button
        if not member.time_online:
            result["replacement_button"] = "online"
        elif not member.time_offline:
            result["replacement_button"] = "offline"

        # breaks_button
        break_obj = instance.get_break_for_user(user)
        if not break_obj:
            replacement_finish = datetime.datetime.combine(instance.date, instance.break_end).astimezone()
            if replacement_finish - datetime.timedelta(minutes=30) >= now:
                result["break_button"] = "create"
        else:
            member_break_start = datetime.datetime.combine(now.date(), break_obj.break_start).astimezone()

            if not member.time_break_start:
                if now + datetime.timedelta(minutes=5) < member_break_start:
                    result["break_button"] = "coming"
                else:
                    result["break_button"] = "start"
            elif not member.time_break_end:
                result["break_button"] = "finish"

        return result


class ReplacementCreateSerializer(InfoModelSerializer):
    group = PrimaryKeyRelatedField(queryset=Group.objects.all())
    members = PrimaryKeyRelatedField(queryset=Member.objects.all(), many=True, allow_null=True, required=False)
    all_group_members = BooleanField(default=False)
    remember_default_data = BooleanField(default=False)

    class Meta:
        model = Replacement
        fields = (
            "id",
            "group",
            "date",
            "break_start",
            "break_end",
            "break_max_duration",
            "min_active",
            "members",
            "all_group_members",
            "remember_default_data",
        )
        extra_kwargs = {
            "break_start": {"required": False, "allow_null": True},
            "break_end": {"required": False, "allow_null": True},
            "break_max_duration": {"required": False, "allow_null": True},
            "min_active": {"required": False, "allow_null": True},
        }

    def create(self, validated_data):
        remember_data = validated_data.pop("remember_default_data", False)
        all_group_members = validated_data.pop("all_group_members", False)

        with transaction.atomic():
            if hasattr(validated_data["group"], "breaks_info"):
                validated_data["group"] = validated_data["group"].breaks_info
            else:
                validated_data["group"] = GroupInfo.objects.create(
                    group=validated_data["group"],
                )

            if all_group_members:
                validated_data.pop("members", list())
                members = validated_data["group"].group.members_info.all()
            else:
                members = validated_data.pop("members")
            instance = super().create(validated_data)

            instance.members.set(members, through_defaults={"status_id": "offline"})

            if remember_data:
                defaults = {
                    "break_start": validated_data["break_start"],
                    "break_end": validated_data["break_end"],
                    "break_max_duration": validated_data["break_max_duration"],
                    "min_active": validated_data["min_active"],
                }
                group = instance.group
                for key, value in defaults.items():
                    setattr(group, key, value)
                group.save()

            return instance

    def validate(self, attrs):
        # Check params
        required_fields = ("break_start", "break_end", "break_max_duration", "min_active")
        for field in required_fields:
            try:
                from_default = getattr(attrs["group"].breaks_info, field)
            except:
                from_default = None

            from_request = attrs.get(field)
            field_data = from_request or from_default

            if not field_data:
                field_name = getattr(self.Meta.model, field).field.verbose_name
                raise ParseError(f"{field_name} - required field.")
            else:
                attrs[field] = field_data

        # Check times
        if attrs.get("break_start") and attrs.get("break_end"):
            if attrs.get("break_start") >= attrs.get("break_end"):
                raise ParseError("The break start time must be less than the end time.")

        # Check duplicates
        if self.Meta.model.objects.filter(group_id=attrs["group"].pk, date=attrs["date"]).exists():
            raise ParseError("Today there is already an active shift.")
        return attrs

    def validate_group(self, value):
        user = self.context["request"].user
        my_groups = Group.objects.my_groups_admin(user)
        if value not in my_groups:
            raise ParseError("You do not have permission to create shifts in this group.")
        return value

    def validate_date(self, value):
        now = timezone.now().date()
        if value < now:
            raise ParseError("The change date must be greater than or equal to the current date.")
        return value

    def validate_break_start(self, value):
        if value.minute % 15 > 0:
            raise ParseError("The start time of the break must be a multiple of 15 minutes.")
        return value

    def validate_break_end(self, value):
        if value.minute % 15 > 0:
            raise ParseError("The end time of the break must be a multiple of 15 minutes.")
        return value


class ReplacementUpdateSerializer(InfoModelSerializer):
    members = PrimaryKeyRelatedField(queryset=Member.objects.all(), many=True, allow_null=True, required=False)
    all_group_members = BooleanField(default=False)
    remember_default_data = BooleanField(default=False)

    class Meta:
        model = Replacement
        fields = (
            "id",
            "date",
            "break_start",
            "break_end",
            "break_max_duration",
            "min_active",
            "members",
            "all_group_members",
            "remember_default_data",
        )

    def update(self, instance, validated_data):
        remember_data = validated_data.pop("remember_default_data", False)
        all_group_members = validated_data.pop("all_group_members", False)

        with transaction.atomic():
            if all_group_members:
                validated_data.pop("members", list())
                members = self.instance.group.members_info.all()
            else:
                members = validated_data.pop("members", None)
            instance = super().update(instance, validated_data)

            if members:
                instance.members.set(members, through_defaults={"status_id": "created"})

            if remember_data:
                defaults = {
                    "break_start": (validated_data.get("break_start") or self.instance.break_start),
                    "break_end": (validated_data.get("break_end") or self.instance.break_end),
                    "break_max_duration": (
                        validated_data.get("break_max_duration") or self.instance.break_max_duration
                    ),
                    "min_active": (validated_data.get("min_active") or self.instance.min_active),
                }
                group = instance.group
                for key, value in defaults.items():
                    setattr(group, key, value)
                group.save()

            return instance

    def validate(self, attrs):
        # Check times

        if attrs.get("break_start") or attrs.get("break_end"):
            break_start = attrs.get("break_start") or self.instance.break_start
            break_end = attrs.get("break_end") or self.instance.break_end
            if break_start >= break_end:
                raise ParseError("The break start time must be less than the end time.")

        # Check duplicates
        if (
            attrs.get("date")
            and self.Meta.model.objects.filter(group_id=self.instance.group.pk, date=attrs["date"])
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise ParseError("Today there is already an active shift.")
        return attrs

    def validate_date(self, value):
        now = timezone.now().date()
        if value < now:
            raise ParseError("The change date must be greater than or equal to the current date.")
        return value

    def validate_break_start(self, value):
        if value.minute % 15 > 0:
            raise ParseError("The start time of the break must be a multiple of 15 minutes.")
        return value

    def validate_break_end(self, value):
        if value.minute % 15 > 0:
            raise ParseError("The end time of the break must be a multiple of 15 minutes.")
        return value


class ReplacementMemberListSerializer(InfoModelSerializer):
    status = DictMixinSerializer()

    class Meta:
        model = ReplacementMember
        fields = ("id", "status")


class ReplacementMemberUpdateSerializer(InfoModelSerializer):
    class Meta:
        model = ReplacementMember
        fields = ("id", "status")

    def validate_status(self, value):
        now = datetime.datetime.now().astimezone().date()
        if self.instance.replacement.date != now:
            raise ParseError("The shift has not yet begun or has already ended.")

        value_code = value.code
        instance_value_code = self.instance.status_id
        if value_code == REPLACEMENT_MEMBER_ONLINE:
            if self.instance.time_offline:
                raise ParseError("You have already completed your shift.")
        elif value == REPLACEMENT_MEMBER_OFFLINE:
            if instance_value_code != REPLACEMENT_MEMBER_ONLINE:
                raise ParseError("Unable to end shift. Check all pending shift activities")
        return value

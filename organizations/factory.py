from django.db.models import Case, When, Q, F, Value

from organizations.models import Offer


class OfferFactory:
    def __init__(self, user):
        self.user = user

    model = Offer

    def org_list(self):
        qs = (
            self.model.objects.select_related("user")
            .prefetch_related("organisation")
            .annotate(
                offer_type=Case(When(~Q(created_by=F("user")), then=Value("sent")), default=Value("received")),
                can_accept=Case(
                    When(Q(offer_type="sent", user_accept__isnull=True, org_accept=False), then=True),
                    When(
                        Q(offer_type="received", user_accept=True, org_accept__isnull=True),
                        then=True,
                    ),
                    default=False,
                ),
                can_reject=Case(
                    When(Q(offer_type="sent", user_accept__isnull=True, org_accept=True), then=True),
                    When(
                        Q(offer_type="received", user_accept=True, org_accept__isnull=True),
                        then=True,
                    ),
                    default=False,
                ),
            )
        )
        return qs

    def user_list(self):
        qs = (
            Offer.objects.select_related("user")
            .prefetch_related("organisation")
            .filter(user=self.user)
            .annotate(
                offer_type=Case(When(Q(created_by=F("user")), then=Value("sent")), default=Value("received")),
                can_accept=Case(
                    When(Q(offer_type=True, org_accept__isnull=True, user_accept=False), then=True),
                    When(Q(offer_type=False, org_accept=True, user_accept__isnull=True), then=True),
                    default=False,
                ),
                can_reject=Case(
                    When(Q(offer_type=True, org_accept__isnull=True, user_accept=True), then=True),
                    When(Q(offer_type=False, org_accept=True, user_accept__isnull=True), then=True),
                    default=False,
                ),
            )
        )
        return qs

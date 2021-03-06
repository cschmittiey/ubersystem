from uber.common import *


class ReportBase:
    def write_row(self, row, out):
        """This method exists for plugins to monkeypatch and/or override."""
        out.writerow(row)


class PersonalizedBadgeReport(ReportBase):
    """
    Generate a CSV file which contains personalized badges with custom printed_names on them

    Deferred badges probably should be printed, since in theory a Deferred badge might be checked in.
    For example, a badge might be marked as Deferred if the attendee name matches a name on our watch list,
    but we might find at the event that they're just a different person with the same name.

    see discussion: https://github.com/magfest/ubersystem/issues/1648
    """
    def __init__(self, include_badge_nums=True):
        self._include_badge_nums = include_badge_nums

    def run(self, out, session, *filters, order_by=None, badge_type_override=None):
        for a in (session.query(sa.Attendee)
                         .filter(sa.Attendee.badge_status != c.INVALID_STATUS, *filters)
                         .order_by(order_by).all()):
            row = [a.badge_num] if self._include_badge_nums else []
            badge_type_label = badge_type_override if badge_type_override else a.badge_type_label
            row += [badge_type_label, a.badge_printed_name or a.full_name]
            self.write_row(row, out)


class PrintedBadgeReport(ReportBase):
    """Generate a CSV file of badges which do not have customized information"""
    def __init__(self, badge_type, include_badge_nums=True):
        self._badge_type = badge_type
        self._include_badge_nums = include_badge_nums

    def run(self, out, session):
        badge_range = c.BADGE_RANGES[self._badge_type]
        for badge_num in range(badge_range[0], badge_range[1] + 1):
            self.write_row([badge_num], out)

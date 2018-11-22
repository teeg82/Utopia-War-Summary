from db import fetch_aggregated_acres


def generate_aggregated_acres_summary():
    aggregated_acres = fetch_aggregated_acres()

    summary = []

    for kingdom in aggregated_acres.keys():
        header = "\n\n** The Kingdom of %s **\n" % kingdom

        provinces = aggregated_acres[kingdom]

        total_land = 0
        total_hits_for = 0
        total_hits_against = 0

        provinces_summary_list = []
        for province in provinces:
            province_name = province['province']
            acres = province['acres']
            acres_str = "+{:,}".format(acres) if acres > 0 else "{:,}".format(acres)

            hits_for = province['hits_for']
            hits_against = province['hits_against']

            total_land += acres
            total_hits_for += hits_for
            total_hits_against += hits_against

            province_line = "{:>10} {:<1} ({:,}/{:,})".format(acres_str, province_name, hits_for, hits_against)
            provinces_summary_list.append(province_line)

        total_land_str = "+{:,}".format(total_land) if total_land > 0 else "{:,}".format(total_land)
        total_land_exchanged = "Total land exchanged: {} ({:,}/{:,})".format(total_land_str, total_hits_for, total_hits_against)
        provinces_summary_list.insert(0, total_land_exchanged)

        summary.append(header + "\n".join(provinces_summary_list))
    return "\n".join(summary)


"""
** Summary **
Total attacks made: 560 (10,858 acres)
-- Traditional march: 459 (10,068 acres)
-- Ambush: 34 (628 acres)
-- Conquest: 11 (162 acres)
-- Raze: 37 (0 acres)
-- Massacre: 2 (781 population)
-- Failed: 17 (3% failure)
-- Uniques: 193
Total attacks suffered: 429 (10,459 acres)
-- Traditional march: 400 (10,207 acres)
-- Ambush: 7 (252 acres)
-- Raze: 10 (0 acres)
-- Massacre: 2 (863 population)
-- Failed: 10 (2.3% failure)
-- Uniques: 169
"""

def generate_totals_summary():
    pass


def render_summary():
    summary = []
    aggregated_acres_summary = generate_aggregated_acres_summary()
    summary.append(aggregated_acres_summary)
    return "\n".join(summary)


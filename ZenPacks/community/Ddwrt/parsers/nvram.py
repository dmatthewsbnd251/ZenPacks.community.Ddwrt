##############################################################################
#
# Copyright (C) Zenoss, Inc. 2008, all rights reserved.
#
# This content is made available according to terms specified in
# License.zenoss under the directory where your Zenoss product is installed.
#
##############################################################################


from Products.ZenRRD.CommandParser import CommandParser
import time

class nvram(CommandParser):

    def processResults(self, cmd, result):
        """
        Process the results of "/usr/sbin/nvram show".
        """

        if cmd.result.output:
            datapointMapInitial = dict()
            for entry in cmd.result.output.splitlines():
                entry_value_pairs = entry.split('=')
                if len(entry_value_pairs) == 2:
                    try:
                        datapointMapInitial[entry_value_pairs[0]] = float(entry_value_pairs[1])
                    except ValueError:
                        datapointMapInitial[entry_value_pairs[0]] = entry_value_pairs[1]


            #extract inbound, outbound, and total transfer bytes by day
            cur_month_stats_key = 'traff-' + time.strftime("%m-%Y")
            cur_month_stats_full = datapointMapInitial.get(cur_month_stats_key, None)
            datapointMapInitial['incoming_day_bytes'] = None
            datapointMapInitial['outgoing_day_bytes'] = None
            datapointMapInitial['total_day_bytes'] = None
            if cur_month_stats_full is not None:
                try:
                    day_stats = dict(zip(['incoming_day', 'outgoing_day'], cur_month_stats_full.split('[')[0].split(' ')[int(time.strftime('%e'))-1].split(':')))
                    datapointMapInitial['incoming_day_bytes'] = long(day_stats['incoming_day'])*1048576
                    datapointMapInitial['outgoing_day_bytes'] = long(day_stats['outgoing_day'])*1048576
                    datapointMapInitial['total_day_bytes'] = datapointMapInitial['outgoing_day_bytes'] + datapointMapInitial['incoming_day_bytes']
                except Exception as e:
                    pass


            #extract total inbound, outbound, and total transfer rate for the month
            datapointMapInitial['incoming_month_bytes'] = None
            datapointMapInitial['outgoing_month_bytes'] = None
            datapointMapInitial['total_month_bytes'] = None
            if cur_month_stats_full is not None:
                try:
                    month_stats = dict(zip(['incoming_month', 'outgoing_month'], cur_month_stats_full.split('[')[1].split(']')[0].split(':')))
                    datapointMapInitial['incoming_month_bytes'] = long(month_stats['incoming_month'])*1048576
                    datapointMapInitial['outgoing_month_bytes'] = long(month_stats['outgoing_month'])*1048576
                    datapointMapInitial['total_month_bytes'] = datapointMapInitial['outgoing_month_bytes'] + datapointMapInitial['incoming_month_bytes']
                except Exception as e:
                    pass


            returnMap = {
                'nvDayBytesIncoming': datapointMapInitial.get('incoming_day_bytes', None),
                'nvDayBytesOutgoing': datapointMapInitial.get('outgoing_day_bytes', None),
                'nvDayBytesTotal': datapointMapInitial.get('total_day_bytes', None),
                'nvMonthBytesIncoming': datapointMapInitial.get('incoming_month_bytes', None),
                'nvMonthBytesOutgoing': datapointMapInitial.get('outgoing_month_bytes', None),
                'nvMonthBytesTotal': datapointMapInitial.get('total_month_bytes', None),
                'nvBytesIncomingRate': datapointMapInitial.get('incoming_month_bytes', None),
                'nvBytesOutgoingRate': datapointMapInitial.get('outgoing_month_bytes', None),
                'nvBytesTotalRate': datapointMapInitial.get('total_month_bytes', None),
            }

            for dp in cmd.points:
                if dp.id in returnMap:
                    result.values.append((dp, returnMap[dp.id]))

        return result

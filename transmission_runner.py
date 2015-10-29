#!/usr/bin/python
#   Copyright (C) 2013-2015 Eluvatar
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from transmission import transmission
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

import argparse

parser = argparse.ArgumentParser(description="Observe happenings")
parser.add_argument('-u','--user', required=True, help='a nation name, email, or web page to identify the user as per item 1 of the NS API Terms of Use: http://www.nationstates.net/pages/api.html#terms')
parser.add_argument('--period', type=float, help='a period in seconds between checks of the world happenings feed. 3.0 by default.', default=3.0)
args = parser.parse_args()
transmission.loop(args.user,6261,period=args.period)

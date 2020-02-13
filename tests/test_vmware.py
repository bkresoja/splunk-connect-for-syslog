# Copyright 2019 Splunk, Inc.
#
# Use of this source code is governed by a BSD-2-clause-style
# license that can be found in the LICENSE-BSD2 file or at
# https://opensource.org/licenses/BSD-2-Clause
import datetime
import random
import pytz

from jinja2 import Environment, environment

from .sendmessage import *
from .splunkutils import *
import random

env = Environment(extensions=['jinja2_time.TimeExtension'])

#vpxd 123 - - Event [3481177] [1-1] [2019-05-23T09:03:36.213922Z] [vim.event.UserLoginSessionEvent] [info] [VSPHERE.LOCAL\svc-vcenter-user] [] [3481177] [User VSPHERE.LOCAL\svc-vcenter-user@192.168.10.10 logged in as pyvmomi Python/2.7.13 (Linux; 4.9.0-7-amd64; x86_64)]
def test_linux_vmware(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "testvmw-{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    mt = env.from_string("{{ mark }}1 {% now 'utc', '%Y-%m-%dT%H:%M:%SZ' %} {{ host }} vpxd {{ pid }} - - Event [3481177] [1-1] [2019-05-23T09:03:36.213922Z] [vim.event.UserLoginSessionEvent] [info] [VSPHERE.LOCAL\svc-vcenter-user] [] [3481177] [User VSPHERE.LOCAL\svc-vcenter-user@192.168.10.10 logged in as pyvmomi Python/2.7.13 (Linux; 4.9.0-7-amd64; x86_64)]\n")
    message = mt.render(mark="<144>", host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=main {{ pid }} sourcetype=\"vmware:vsphere:esx\" | head 2")
    search = st.render(host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#<46>1 2019-10-24T21:00:02.403Z {{ host }} NSXV 5996 - [nsxv@6876 comp="nsx-manager" subcomp="manager"] Invoking EventHistoryCollector.readNext on session[52db61bf-9c30-1e1f-5a26-8cd7e6f9f552]52032c51-240a-7c30-cd84-4b4246508dbe, operationID=opId-688ef-9725704
def test_linux_vmware_nsx_ietf(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "testvmw-{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    mt = env.from_string("{{ mark }}1 {% now 'utc', '%Y-%m-%dT%H:%M:%SZ' %} {{ host }} NSX - SYSTEM [nsx@6876 comp=\"nsx-manager\" errorCode=\"MP4039\" subcomp=\"manager\"] Connection verification failed for broker '10.160.108.196'. Marking broker unhealthy.\n")
    message = mt.render(mark="<144>", host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=main host={{ host }} sourcetype=\"vmware:vsphere:nsx\" | head 2")
    search = st.render(host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

#
def test_linux_vmware_nsx_fw(record_property, setup_wordlist, setup_splunk, setup_sc4s):
    host = "testvmw-{}-{}".format(random.choice(setup_wordlist), random.choice(setup_wordlist))
    pid = random.randint(1000, 32000)

    mt = env.from_string("{{ mark }} {% now 'local', '%b %d %H:%M:%S' %} {{ host }} dfwpktlogs: {{ pid }} INET match PASS domain-c7/1001 IN 60 TCP 10.33.24.50/45926->10.33.24.9/8140 S\n")
    message = mt.render(mark="<144>", host=host, pid=pid)

    sendsingle(message, setup_sc4s[0], setup_sc4s[1][514])

    st = env.from_string("search earliest=-1m@m latest=+1m@m index=main host={{ host }} {{ pid }} sourcetype=\"vmware:vsphere:nsx\" | head 2")
    search = st.render(host=host, pid=pid)

    resultCount, eventCount = splunk_single(setup_splunk, search)

    record_property("host", host)
    record_property("resultCount", resultCount)
    record_property("message", message)

    assert resultCount == 1

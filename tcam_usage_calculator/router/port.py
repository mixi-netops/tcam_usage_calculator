from ..util import err


protocol_name_to_num = {
    "afs": 1483, "bgp": 179, "biff": 512, "bootpc": 68, "bootps": 67, "chargen": 19, "cmd": 514,
    "cvspserver": 2401, "daytime": 13, "dhcp": 67, "discard": 9, "dnsix": 195, "domain": 53, "echo": 7,
    "eklogin": 2105, "ekshell": 2106, "exec": 512, "finger": 79, "ftp": 21, "ftp-data": 20, "gopher": 70,
    "hostname": 101, "http": 80, "https": 443, "ident": 113, "imap": 143, "irc": 194, "isakmp": 500,
    "kerberos-sec": 88, "klogin": 543, "kpasswd": 761, "krb-prop": 754, "krbupdate": 760, "kshell": 544,
    "ldap": 389, "ldp": 646, "login": 513, "lpd": 515, "mobile-ip": 434, "mobileip-agent": 434,
    "mobilip-mn": 435, "msdp": 639, "nameserver": 42, "netbios-dgm": 138, "netbios-ns": 137, "netbios-ssn": 139,
    "nfsd": 2049, "nntp": 119, "ntalk": 518, "ntp": 123, "pim-auto-rp": 496, "pop2": 109, "pop3": 110,
    "pptp": 1723, "printer": 515, "radacct": 1813, "radius": 1812, "rip": 520, "rkinit": 2108, "smtp": 25,
    "snmp": 161, "snmptrap": 162, "snpp": 444, "socks": 1080, "ssh": 22, "sunrpc": 111, "syslog": 514,
    "tacacs": 49, "tacacs-ds": 65, "talk": 517, "telnet": 23, "tftp": 69, "time": 37, "timed": 525, "uucp": 540,
    "who": 513, "whois": 43, "www": 80, "xdmcp": 177, "zephyr-clt": 2103, "zephyr-hm": 2104, "zephyr-srv": 2102
}


class Port:
    """
    name: String
        port name.
        ex) 'https'

    translate port name to number.
    If the name is a number, it returns as is.
    """
    @staticmethod
    def translate_name2number(name):
        if name.isdigit():
            return name

        try:
            return protocol_name_to_num[name]
        except KeyError:
            err(name + ' protocol is an unknown protocol name.')

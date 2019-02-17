from elasticsearch_dsl import DocType, Text, Date, Integer, Float, Ip, \
    Keyword, GeoPoint, Boolean


class Token(DocType):
    username = Keyword()
    token = Keyword()
    expires = Date()
    read = Boolean()
    write = Boolean()
    revoked = Boolean()
    acl = Keyword()
    groups = Keyword()
    admin = Boolean()
    last_activity_at = Date()

    class Meta:
        index = 'tokens'


class Indicator(DocType):
    indicator = Keyword()
    indicator_ipv4 = Ip()
    indicator_ipv4_mask = Integer()
    indicator_ipv6 = Keyword()
    indicator_ipv6_mask = Integer()
    group = Keyword()
    itype = Keyword()
    tlp = Keyword()
    provider = Keyword()
    portlist = Text()
    asn = Float()
    asn_desc = Text()
    cc = Text(fields={'raw': Keyword()})
    protocol = Text(fields={'raw': Keyword()})
    reporttime = Date()
    last_at = Date()
    first_at = Date()
    confidence = Integer()
    probability = Float()
    timezone = Text()
    city = Text(fields={'raw': Keyword()})
    description = Keyword()
    tags = Keyword(multi=True, fields={'raw': Keyword()})
    rdata = Keyword()
    count = Integer()
    message = Text(multi=True)
    location = GeoPoint()

from elasticsearch_dsl import Document, Text, Date, Integer, Float, Ip, Keyword, GeoPoint, Boolean


class Token(Document):
    class Index:
        name = 'tokens'
        doc_type = 'token'

    class Meta:
        doc_type = 'token'

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
    created_at = Date()


class Indicator(Document):

    class Index:
        name = 'indicators-*'
        doc_type = 'indicator'

    class Meta:
        doc_type = 'indicator'

    indicator = Keyword()
    indicator_ipv4 = Ip()
    indicator_ipv4_mask = Integer()
    indicator_ipv6 = Ip()
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
    region = Keyword()
    latitude = Float()
    longitude = Float()
    ns = Keyword()
    mx = Keyword()
    reported_at = Date()
    last_at = Date()
    first_at = Date()
    created_at = Date()

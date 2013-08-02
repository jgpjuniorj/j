import lxml.etree


def el2dict(parent_el):
    """convert a very simple element into a dictionary"""
    return dict((el.tag, el.text) for el in parent_el.getchildren())


def parse_xml(xml):

    root = lxml.etree.fromstring(xml)

    deviceid = root.xpath('/REQUEST/DEVICEID')[0].text
    
    content = root.xpath('/REQUEST/CONTENT')[0]
    cx = content.xpath
    
    logdate = cx('ACCESSLOG/LOGDATE')[0].text
    bios_el = cx('BIOS')[0]
    
    bios = el2dict(bios_el)
    
    other = {}
    
    for tag in [
            'CONTROLLERS', 'CPUS', 'DRIVES', 'ENVS',
            'INPUTS', 'NETWORKS', 'PROCESSES', 'SOFTWARES',
            'SOUNDS', 'STORAGES', 'USBSERVICES'
            ]:
        other[tag] = [
            el2dict(el)
            for el in cx(tag)
            ]
    
    hardware = el2dict(cx('HARDWARE')[0])
    
    operating_system = el2dict(cx('OPERATINGSYSTEM')[0])

    return deviceid, logdate, bios, hardware, operating_system, other


def parse_computer_item(obj):
    return parse_xml(obj.ocs)



#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def search(client, string):
    pattern = re.compile(client)
    return re.search(pattern, string)


def check_mobile(request):
    """
    demo :
        def is_from_mobile():
            if check_mobile(request):
                return 'mobile'
            else:
                return 'pc'
    :param request:
    :return:
    """
    user_agent = request.META.get('HTTP_USER_AGENT', None)
    _long_matches = r'googlebot-mobile|android|avantgo|blackberry|blazer|elaine' \
                    r'|hiptop|ip(hone|od)|kindle|midp|mmp|mobile|o2|opera mini|' \
                    r'palm( os)?|pda|plucker|pocket|psp|smartphone|symbian|treo|' \
                    r'up\.(browser|link)|vodafone|wap|windows ce; (iemobile|ppc)|' \
                    r'xiino|maemo|fennec'
    _long_matches = re.compile(_long_matches, re.IGNORECASE)
    _short_matches = r'1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|' \
                     r'ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|' \
                     r'aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|' \
                     r'be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|' \
                     r'c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|' \
                     r'da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|' \
                     r'el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|' \
                     r'fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|' \
                     r'haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-|' \
                     r' |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|' \
                     r'ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|' \
                     r'kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|' \
                     r'\/(k|l|u)|50|54|e\-|e\/|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|' \
                     r'ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(di|rc|ri)|mi(o8|oa|ts)|' \
                     r'mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|' \
                     r'n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|' \
                     r'on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|' \
                     r'pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|' \
                     r'po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|' \
                     r'i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|' \
                     r'ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|' \
                     r'shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|' \
                     r'sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|' \
                     r'tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|' \
                     r'tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|' \
                     r'\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|' \
                     r'webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\-|2|g)|yas\-|your|zeto|zte\-'
    _short_matches = re.compile(_short_matches, re.IGNORECASE)

    if _long_matches.search(user_agent) != None:
        return True
    user_agent = user_agent[0:4]
    if _short_matches.search(user_agent) != None:
        return True
    return False


def split_ua(request):
    if not request or "HTTP_USER_AGENT" not in request.META:
        return {"device_type":"pc"}

    ua = request.META['HTTP_USER_AGENT']
    tmp_ua = ua.lower()

    if "mozilla" in tmp_ua or "safari" in tmp_ua:
        if check_mobile(request):
            return {"device_type":"pc", "app_version":'wlb_h5',
                "channel_id":'', "model":'',
                "os_version":'', "network":''}
        else:
            return {"device_type":"pc"}

    arr = ua.split("/")
    if len(arr) < 5:
        return {"device_type":"pc"}

    dt = arr[1].lower()
    if "android" in dt:
        device_type = "android"
    elif "iphone" in dt or "ipad" in dt:
        device_type = "ios"
    else:
        device_type = "pc"

    return {"device_type":device_type, "app_version":arr[0],
            "channel_id":arr[2], "model":arr[1],
            "os_version":arr[3], "network":arr[4]}


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

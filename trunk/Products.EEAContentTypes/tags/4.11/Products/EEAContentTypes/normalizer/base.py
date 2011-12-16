""" Base normalizer
"""
# Latin characters with accents, etc.
mapping = {
    138 : u's', 140 : u'O', 142 : u'z', 154 : u's', 156 : u'o', 158 : u'z',
    159 : u'Y', 192 : u'A', 193 : u'A', 194 : u'A', 195 : u'a', 197 : u'Aa',
    199 : u'C', 200 : u'E', 201 : u'E', 202 : u'E', 203 : u'E', 204 : u'I',
    205 : u'I', 206 : u'I', 207 : u'I', 208 : u'Th', 209 : u'N', 210 : u'O',
    211 : u'O', 212 : u'O', 213 : u'O', 215 : u'x', 216 : u'O', 217 : u'U',
    218 : u'U', 219 : u'U', 222 : u'th', 221 : u'Y', 225 : u'a', 226 : u'a',
    227 : u'a', 229 : u'aa', 231 : u'c', 232 : u'e', 233 : u'e', 234 : u'e',
    235 : u'e', 236 : u'i', 237 : u'i', 238 : u'i', 239 : u'i', 240 : u'th',
    241 : u'n', 242 : u'o', 243 : u'o', 244 : u'o', 245 : u'o', 248 : u'oe',
    249 : u'u', 250 : u'u', 251 : u'u', 253 : u'y', 254 : u'Th', 255 : u'y',
#
# Bulgarian character mapping
    1040: u'A', 1041: u'B', 1042: u'V', 1043: u'G', 1044: u'D', 1045: u'E',
    1046: u'ZH', 1047: u'Z', 1048: u'I', 1049: u'Y', 1050: u'K', 1051: u'L',
    1052: u'M', 1053: u'N', 1054: u'O', 1055: u'P', 1056: u'R', 1057: u'S',
    1058: u'T', 1059: u'U', 1060: u'F', 1061: u'H', 1062: u'TS', 1063: u'CH',
    1064: u'SH', 1065: u'SHT', 1066: u'A', 1068: u'Y', 1070: u'YU', 1071: u'YA',
    1072: u'a', 1073: u'b', 1074: u'v', 1075: u'g', 1076: u'd', 1077: u'e',
    1078: u'zh', 1079: u'z', 1080: u'i', 1081: u'y', 1082: u'k', 1083: u'l',
    1084: u'm', 1085: u'n', 1086: u'o', 1087: u'p', 1088: u'r', 1089: u's',
    1090: u't', 1091: u'u', 1092: u'f', 1093: u'h', 1094: u'ts',
    1095: u'ch', 1096: u'sh', 1097: u'sht', 1098: u'a', 1100: u'y',
    1102: u'yu', 1103: u'ya',
#
# German character mapping
    196 : u'AE', 198 : u'AE', 214 : u'OE', 220 : u'UE', 223 : u'ss', 224 : u'a',
    228 : u'ae', 230 : u'ae', 246 : u'oe', 252 : u'ue',
#
# Greek character mapping
    902: u'A', 904: u'E', 905: u'H', 906: u'I', 908: u'O', 910: u'Y', 911: u'O',
    912: u'i', 913: u'A', 914: u'B', 915: u'G', 916: u'D', 917: u'E', 918: u'Z',
    919: u'I', 920: u'Th', 921: u'I', 922: u'K',
    923: u'L', 924: u'M', 925: u'N',
    926: u'Ks', 927: u'O', 928: u'P', 929: u'R', 931: u'S',
    932: u'T', 933: u'Y',
    934: u'F', 935: u'Ch', 936: u'Ps', 937: u'O', 938: u'I',
    939: u'Y', 940: u'a',
    941: u'e', 942: u'i', 943: u'i', 944: u'y', 945: u'a',
    946: u'b', 947: u'g',
    948: u'd', 949: u'e', 950: u'z', 951: u'i', 952: u'th',
    953: u'i', 954: u'k',
    955: u'l', 956: u'm', 957: u'n', 958: u'ks', 959: u'o',
    960: u'p', 961: u'r',
    962: u's', 963: u's', 964: u't', 965: u'y', 966: u'f',
    967:'ch', 968: u'ps',
    969: u'o', 970: u'i', 971: u'y', 972: u'o', 973: u'y', 974: u'o',
#
# French character mapping
    339: u'oe',
#
# Polish character mapping
    321 : u'L', 322 : u'l',
#
# Turkish character mapping
    286 : u'G', 287 : u'g', 304 : u'I', 305 : u'i', 350 : u'S', 351 : u's',
}

def mapUnicode(text):
    """
    This method is used for replacement of special characters found in a mapping
    before baseNormalize is applied.
    """
    if not isinstance(text, unicode):
        try:
            text = text.decode('utf-8')
        except Exception:
            return text

    return text.translate(mapping)

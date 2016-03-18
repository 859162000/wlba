# encoding=utf-8
<<<<<<< HEAD
from wanglibao_pay.models import Bank, Card 
=======
from wanglibao_pay.models import Bank
>>>>>>> 25c1a6e... feature: check bank card info for yee, finish data
from django.core.management.base import BaseCommand

bank_cards_info = """{
"北京农村商业银行": "620088,621066,621067,621068,621560,622138,623265",
"光大银行": "303,90030,303375,303764,303765,303775,356837,356838,356839,356840,406252,406254,425862,481699,486497,524090,543159,620085,620518,620535,621381,621489,621490,621491,621492,622161,622570,622650,622655,622657,622658,622659,622660,622661,622662,622663,622664,622665,622666,622667,622668,622669,622670,622671,622672,622673,622674,622685,622687,622801,623155,623156,623157,623158,623159,623253,625339,625975,625976,625977,625978,625979,625980,625981,628201,628202",
"平安银行": "356868,356869,412962,412963,415752,415753,435744,435745,483536,526855,528020,531659,602907,620010,621626,622155,622156,622157,622298,622525,622526,622535,622536,622538,622539,622983,622986,622989,623058,623269,625360,625361,625823,625825,627066,627067,627068,627069,628296,998800,998801,998802",
"工商银行": "9558,45806,53098,356879,356880,356881,356882,360883,360884,370246,370247,370248,370249,370267,374738,374739,402791,427010,427018,427019,427020,427028,427029,427030,427038,427039,427062,427064,438125,438126,451804,451810,451811,458065,458071,458441,489734,489735,489736,510529,513685,524047,524091,524374,525498,526836,528856,530970,530985,530990,543098,544210,548259,548943,550213,558360,620030,620050,620054,620058,620086,620094,620101,620114,620124,620131,620142,620143,620146,620148,620149,620183,620184,620185,620186,620187,620200,620302,620402,620403,620404,620405,620406,620407,620408,620409,620410,620411,620412,620502,620503,620512,620516,620561,620602,620604,620607,620609,620611,620612,620704,620706,620707,620708,620709,620710,620711,620712,620713,620714,620802,620902,620904,620905,621001,621102,621103,621105,621106,621107,621202,621203,621204,621205,621206,621207,621208,621209,621210,621211,621218,621225,621226,621227,621240,621281,621288,621300,621302,621303,621304,621305,621306,621307,621309,621311,621313,621315,621317,621370,621371,621372,621373,621374,621375,621376,621377,621378,621379,621402,621404,621405,621406,621407,621408,621409,621410,621414,621423,621428,621433,621434,621464,621475,621476,621502,621511,621558,621559,621602,621603,621604,621605,621606,621607,621608,621609,621610,621611,621612,621613,621614,621615,621616,621617,621618,621670,621719,621720,621721,621722,621723,621724,621730,621731,621732,621733,621734,621749,621750,621761,621762,621765,621781,621804,621807,621813,621814,621817,621901,621903,621904,621905,621906,621907,621908,621909,621910,621911,621912,621913,621914,621915,622002,622003,622004,622005,622006,622007,622008,622010,622011,622012,622013,622015,622016,622017,622018,622019,622020,622102,622103,622104,622105,622110,622111,622114,622158,622159,622171,622200,622202,622203,622206,622208,622210,622211,622212,622213,622214,622215,622220,622223,622224,622225,622227,622229,622230,622231,622232,622233,622234,622235,622236,622237,622238,622239,622240,622245,622246,622302,622303,622304,622305,622306,622307,622308,622309,622313,622314,622315,622317,622402,622403,622404,622502,622504,622505,622509,622510,622513,622517,622597,622599,622604,622605,622606,622703,622706,622715,622806,622889,622902,622903,622904,622910,622911,622912,622913,622926,622927,622928,622929,622930,622931,622944,622949,623002,623006,623008,623011,623012,623014,623015,623062,623100,623202,623229,623260,623271,623272,623301,623321,623335,623400,623500,623602,623700,623803,623901,624000,624100,624200,624301,624402,624518,624580,625017,625018,625019,625021,625022,625113,625114,625115,625116,625160,625161,625162,625309,625330,625331,625332,625650,625651,625708,625709,625801,625858,625859,625860,625865,625866,625899,625900,625914,625915,625916,625917,625918,625921,625922,625923,625924,625925,625926,625927,625928,625929,625930,625933,625939,625941,625942,625986,625987,628286,628288,900000,900010,955880,955881,955882,955888",
"东亚银行": "621411,622265,622266,622365,622372,622471,622472,622933,622938,622943,623031,623318,625972,625973",
"兴业银行": "90592,438588,438589,451289,451290,461982,486493,486494,486861,523036,524070,527414,528057,548738,549633,552398,621245,621689,622571,622572,622573,622591,622592,622593,622901,622902,622908,622909,622922,625082,625083,625084,625085,625086,625087,625353,625356,625960,625961,625962,625963,628212,966666",
"农业银行": "103,49102,53591,95595,95596,95597,95598,95599,403361,404117,404118,404119,404120,404121,463758,491020,491021,491022,491023,491024,491025,491026,491027,491028,491029,514027,519412,519413,520082,520083,535910,535911,535912,535913,535914,535915,535916,535917,535918,535919,544243,548478,552599,558730,620059,620501,621282,621336,621619,621671,622820,622821,622822,622823,622824,622825,622826,622827,622828,622830,622836,622837,622838,622839,622840,622841,622843,622844,622845,622846,622847,622848,622849,623018,623206,625170,625171,625336,625653,625826,625827,625996,625997,625998,628268,628269,628346,634910,635359,955950,955951,955952,955953,955954,955955,955956,955957,955958,955959,955960,955961,955962,955963,955964,955965,955966,955967,955968,955969,955970,955971,955972,955973,955974,955975,955976,955977,955978,955979,955980,955981,955982,955983,955984,955985,955986,955987,955988,955989,955990,955991,955992,955993,955994,955995,955996,955997,955998,955999",
"上海银行": "356827,356828,356829,356830,402673,402674,438600,486466,519498,519961,520131,524031,548838,620522,621005,621050,621243,622148,622149,622172,622267,622268,622269,622278,622279,622300,622468,622892,622985,622987,623183,623185,625099,625180,625350,625351,625352,625839,625953,628230,940021",
"邮政储蓄银行": "518905,620062,620529,621095,621096,621098,621285,621582,621599,621622,621674,621797,621798,621799,622150,622151,622180,622181,622182,622187,622188,622189,622199,622810,622811,622812,622835,623218,623219,623686,623698,623699,625367,625368,625603,625605,625919,628310,955100",
"浙商银行": "621019,622309,625821",
"渤海银行": "621268,621453,622684,622884,625122",
"杭州银行": "",
"中国银行": "356833,356835,377677,409665,409666,409667,409668,409669,409670,409671,409672,438088,456351,512315,512316,512411,512412,514957,514958,518377,518378,518379,518474,518475,518476,524864,524865,525745,525746,547766,552742,553131,558868,558869,601382,620019,620025,620026,620035,620040,620061,620202,620203,620210,620211,620513,620514,620531,621041,621212,621231,621248,621249,621256,621283,621293,621294,621297,621330,621331,621332,621333,621334,621342,621343,621364,621394,621395,621568,621569,621620,621638,621648,621660,621661,621662,621663,621665,621666,621667,621668,621669,621672,621725,621741,621756,621757,621758,621759,621782,621785,621786,621787,621788,621789,621790,622273,622274,622346,622347,622348,622380,622479,622480,622752,622753,622754,622755,622756,622757,622758,622759,622760,622761,622762,622763,622764,622765,622770,622771,622772,622788,622789,622790,623040,623184,623208,623263,623309,623569,623571,623572,623573,623575,623586,624405,625140,625333,625337,625338,625568,625834,625905,625906,625907,625908,625909,625910,626200,627025,627026,627027,627028,628312,628313,628388",
"华夏银行": "523959,528708,528709,539867,539868,620552,621222,622630,622631,622632,622633,622636,622637,622638,623020,623021,623022,623023,623557,625967,625968,625969,628318,999999",
"中信银行": "356390,356391,356392,376966,376968,376969,400360,403391,403392,403393,404157,404158,404159,404171,404172,404173,404174,433666,433667,433669,433670,433671,433680,442729,442730,514906,518212,520108,556617,558916,620082,620527,621767,621768,621769,621770,621771,621772,621773,622453,622456,622459,622678,622679,622680,622688,622689,622690,622691,622692,622696,622698,622766,622767,622768,622916,622918,622919,622998,622999,623280,623328,623397,624303,628206,628208,628209,628370,628371,628372,968807,968808,968809",
"上海浦东发展银行": "84301,84336,84342,84361,84373,84380,84385,84390,87000,87010,87030,87040,87050,356850,356851,356852,377187,404738,404739,456418,498451,515672,517650,525998,620530,621275,621351,621352,621390,621791,621792,621793,621795,621796,622176,622177,622228,622276,622277,622500,622516,622517,622518,622519,622520,622521,622522,622523,622693,623250,625831,625833,625957,625958,625970,625971,625993,628221,628222,984301,984303",
"上海农村商业银行": "",
"招商银行": "95555,356885,356886,356887,356888,356889,356890,370285,370286,370287,370289,402658,410062,439188,439225,439226,439227,468203,479228,479229,512425,518710,518718,521302,524011,545619,545620,545621,545623,545947,545948,552534,552587,620520,621286,621299,621483,621485,621486,622575,622576,622577,622578,622579,622580,622581,622582,622588,622598,622609,623126,623136,623262,625802,625803,628262,628290,628362,690755",
"南京银行": "621259,621777,622303,622305,622595,622596,628242",
"建设银行": "53242,53243,356895,356896,356899,421349,434061,434062,436718,436728,436738,436742,436745,436748,453242,489592,491031,524094,526410,531693,532424,532450,532458,544033,544887,545324,549103,552245,552801,553242,554403,557080,558895,559051,589970,620060,620107,621080,621081,621082,621083,621084,621284,621466,621467,621487,621488,621499,621598,621621,621673,621700,622166,622168,622280,622381,622382,622675,622676,622677,622700,622707,622708,622725,622728,622966,622988,623094,623211,623251,623350,623668,623669,624329,624412,625362,625363,625955,625956,625964,625965,625966,628266,628316,628317,628366",
"广发银行": "9111,406365,406366,428911,436768,436769,487013,491032,491034,491035,491036,491037,491038,518364,520152,520382,528931,548844,552794,558894,620037,621462,622555,622556,622557,622558,622559,622560,622568,623259,623506,625071,625072,625805,625806,625807,625808,625809,625810,628259,628260,685800",
"深圳发展银行": "",
"民生银行": "356856,356857,356858,356859,377152,377153,377155,377158,407405,415599,421393,421865,421869,421870,421871,427570,427571,464580,464581,472067,472068,512466,517636,523952,528948,545217,545392,545393,545431,545447,552288,553161,556610,621399,621691,622600,622601,622602,622603,622615,622616,622617,622618,622619,622620,622621,622622,622623,623198,623255,623258,623683,625188,625911,625912,625913,628258,900003",
"北京银行": "421317,422160,422161,522001,602969,621030,621420,621468,622163,622851,622852,622853,623111,623561,623562,625816,628203",
"交通银行": "4055,4910,5378,6014,49104,53783,405512,434910,458123,458124,520169,521899,522964,552853,601428,620013,620021,620521,621002,621069,621335,621436,622250,622251,622252,622253,622254,622255,622256,622257,622258,622259,622260,622261,622262,622284,622285,622656,623261,625028,625029,628216,628218,664055,664910,665378,666014,955590,955591,955592,955593",
}"""

<<<<<<< HEAD
bank_cards = eval(bank_cards_info)
def insert_bank_cards():
=======
def insert_bank_cards():
    bank_cards = eval(bank_cards_info)
>>>>>>> 25c1a6e... feature: check bank card info for yee, finish data
    for b, c in bank_cards.items():
        try:
            bank = Bank.objects.get(name=b)
            bank.cards_info = c
            bank.save()
        except Exception, e:
            print e
            print b, c

<<<<<<< HEAD
def check_card(card_no, bank_name):
    cards = bank_cards[bank_name].split(',')
    for card in cards:
        if card and card_no.startswith(card):
            return True
    return False

def check_cards():
    cards = Card.objects.filter(is_bind_yee=True).all()
    for card in cards:
        try:
            if not check_card(card.no, card.bank.name):
                print card.no, card.bank.name
        except Exception, error :
                print error, card.no, card.bank.name


class Command(BaseCommand):
    def handle(self, *args, **options):
        insert_bank_cards()
=======
class Command(BaseCommand):
    def handle(self):
        insert_bank_cards()

if __name__ == '__main__':
    insert_bank_cards()
>>>>>>> 25c1a6e... feature: check bank card info for yee, finish data

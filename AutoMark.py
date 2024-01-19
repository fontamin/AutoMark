import os
import fontforge as ff
import argparse

parser = argparse.ArgumentParser(prog='AutoMark',description='AutoMark is a FontForge script to add mark feature and anchor placement for Arabic glyphs. more information on github page: https://github.com/fontamin/AutoMark')
parser.add_argument('input_file', help='a sfd or font file name(with format) or pathname')
parser.add_argument('output_file', help='an output font file name(with format) or pathname')
parser.add_argument('--normalized_mark_to_mark_gap', help='normalized(will multiplied in font em size) distance of mark to mark glyphs(default=0.04)', type = float, default=0.04, metavar='')
parser.add_argument('--normalized_mark_to_base_gap', help='normalized(will multiplied in font em size) distance of mark to base glyphs(default=0.12)', type = float, default=0.12, metavar='')
parser.add_argument('--normalized_depth_in_extrema', help='normalized(will multiplied in font em size) y_extrema substract mostly used for hamza(default=0.08)', type = float, default=0.08, metavar='')
parser.add_argument('--kaf_slop_tolerance', help='the error to find break point of kaf slope(default=0.2)', type = float, default=0.2, metavar='')
parser.add_argument('--normalized_ignore_left_shift', help='to aviod left points of glyph(default=0.05)', type = float, default=0.05, metavar='')
parser.add_argument('--normalized_ignore_right_shift', help='to aviod right points of glyph(default=0.05)', type = float, default=0.05, metavar='')
parser.add_argument('--double_ligature_divide_ratio', help='divide ligature width ratio to find extrema points(default=0.5)', type = float, default=0.5, metavar='')
parser.add_argument('--normalized_y_extrema_avarge_tolerance_ratio', help='normalized tolerance ratio which is multiplied to font em size and used to check if points are in valid range to calculate avarage y extrema point or find vertical side-most contour(s) mid point(default=0.01)', type = float, default=0.01, metavar='')
parser.add_argument('--normalized_BIG_y_extrema_avarge_tolerance_ratio', help='same as normalized_y_extrema_avarge_tolerance_ratio, but multiply directly in y_extrema and include wider vertical range(default=0.5)', type = float, default=0.5, metavar='')
parser.add_argument('--ignore_connection_circle_raduce_factor', help='factor to multiply strok height to find radius of the circle placed on two side of bounding box to remove points near the connections(default=0.5)', type = float, default=0.5, metavar='')
args = parser.parse_args()
normalized_mark_to_mark_gap = args.normalized_mark_to_mark_gap
normalized_mark_to_base_gap = args.normalized_mark_to_base_gap
normalized_depth_in_extrema = args.normalized_depth_in_extrema
kaf_slop_tolerance = args.kaf_slop_tolerance
normalized_y_extrema_avarge_tolerance_ratio = args.normalized_y_extrema_avarge_tolerance_ratio
normalized_ignore_left_shift = args.normalized_ignore_left_shift
normalized_ignore_right_shift = args.normalized_ignore_right_shift
double_ligature_divide_ratio = args.double_ligature_divide_ratio
normalized_BIG_y_extrema_avarge_tolerance_ratio = args.normalized_BIG_y_extrema_avarge_tolerance_ratio
ignore_connection_circle_raduce_factor = args.ignore_connection_circle_raduce_factor
top_mark_glyphs = [0x0610,0x0611,0x0612,0x0613,0x0614,0x0615,0x0616,0x0617,0x0618,0x0619,0x064B,0x064C,0x064E,0x064F,0x0651,0x0652,0x0653,0x0654,0x0657,0x0658,0x0659,0x065A,0x065B,0x065D,0x065E,0x0670,0x06D6,0x06D7,0x06D8,0x06D9,0x06DA,0x06DB,0x06DC,0x06DF,0x06E0,0x06E1,0x06E2,0x06E4,0x06E7,0x06E8,0x06EB,0x06EC]
top_ligature_mark_glyphs = []
bottom_mark_glyphs = [0x061A,0x064D,0x0650,0x0655,0x0656,0x065C,0x065F,0x06E3,0x06EA,0x06ED]
bottom_ligature_mark_glyphs = []
base_glyphs_dict ={

##avarage_extrema: avarage of all y extrema points between (most-valued y exreama) and (most-valued y exreama - y_extrema_avarge_tolerance).
##topmost_contours_mid_point: x:middle contour(s) bounding-box include points placed in range of (most-valued maximum y) and (most-valued maximum y - y_extrema_avarge_tolerance).
##                            y:avarage of maximum y points witch satisfie the above condition.
##bottommost_contours_mid_point: x:middle contour(s) bounding-box include points placed in range of (most-valued minimum y) and (most-valued minimum y + y_extrema_avarge_tolerance).
##                               y:avarage of minimum y points witch satisfie the above condition.
##avarage_topmost_contour_mid_point: x:middle point of topmost contour. contours comparing with their on-curve points y coordination.
##                                   y:maximum point
##avarage_bottommost_contour_mid_point: x:middle point of bottommost contour. contours comparing with their on-curve points y coordination.
##                                      y:minimum point
##bottommost_contour_mid_point: x:bottommost_contour_mid_point
##                              y:minimum
##topmost_contour_mid_point: x:topmost_contour_mid_point
##                           y:maximum
##(closer): every perferance with this suffix radiuss y_extrema absolute value as much as depth_in_extrema.(mostly used in glyphs including hamza)
##
##structure: unicode_codepoint:"top:glyph_top_Anchor_placement_perferance|bottom:glyph_bottom_Anchor_placement_perferance"

0x0620:"top:mid|bottom:bottommost_contour_mid_point",                                          #ؠ
0x0621:"top:avarage_extrema|bottom:mid",                                                       #ء
0x0622:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #آ
0x0623:"top:topmost_contour_mid_point(closer)|bottom:avarage_extrema",                         #أ
0x0624:"top:topmost_contour_mid_point(closer)|bottom:mid",                                     #ؤ
0x0625:"top:avarage_extrema|bottom:bottommost_contour_mid_point(closer)",                      #إ
0x0626:"top:topmost_contour_mid_point(closer)|bottom:avarage_extrema",                         #ئ
0x0627:"top:avarage_extrema|bottom:avarage_extrema",                                           #ا
0x0628:"top:mid|bottom:avarage_bottommost_contour_mid_point",                                  #ب
0x0629:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ة
0x062A:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ت
0x062B:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ث
0x062C:"top:mid|bottom:avarage_extrema",                                                       #ج
0x062D:"top:mid|bottom:avarage_extrema",                                                       #ح
0x062E:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #خ
0x062F:"top:topmost_slope_mid|bottom:avarage_extrema",                                         #د
0x0630:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ذ
0x0631:"top:topmost_slope_mid|bottom:mid",                                                     #ر
0x0632:"top:topmost_contours_mid_point|bottom:mid",                                            #ز
0x0633:"top:BIG_y_extrema(after_x_bottom_extrema)|bottom:avarage_extrema",                     #س
0x0634:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ش
0x0635:"top:avarage_extrema|bottom:avarage_extrema",                                           #ص
0x0636:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ض
0x0637:"top:avarage_extrema_ignore_left|bottom:mid",                                           #ط
0x0638:"top:avarage_topmost_contour_mid_point|bottom:mid",                                     #ظ
0x0639:"top:avarage_extrema|bottom:avarage_extrema",                                           #ع
0x063A:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #غ
0x063B:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ػ
0x063C:"top:kaf|bottom:avarage_extrema",                                                       #ؼ
0x063D:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ؽ
0x063E:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ؾ
0x063F:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ؿ
0x0640:"top:mid|bottom:mid",                                                                   #ـ
0x0641:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ف
0x0642:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ق
0x0643:"top:avarage_topmost_contour_mid_point(closer)|bottom:avarage_extrema",                 #ك
0x0644:"top:mid|bottom:avarage_extrema",                                                       #ل
0x0645:"top:avarage_extrema|bottom:avarage_extrema_ignore_left",                               #م
0x0646:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ن
0x0647:"top:mid|bottom:avarage_extrema",                                                       #ه
0x0648:"top:avarage_extrema|bottom:mid",                                                       #و
0x0649:"top:mid|bottom:avarage_extrema",                                                       #ى
0x064A:"top:mid|bottom:bottommost_contours_mid_point",                                         #ي
0x066E:"top:mid|bottom:avarage_extrema",                                                       #ٮ
0x066F:"top:avarage_extrema|bottom:avarage_extrema",                                           #ٯ
0x0671:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ٱ
0x0672:"top:topmost_contours_mid_point(closer)|bottom:avarage_extrema",                        #ٲ
0x0673:"top:avarage_extrema|bottom:bottommost_contour_mid_point(closer)",                      #ٳ
0x0674:"top:topmost_contour_mid_point(closer)|bottom:mid",                                     #ٴ
0x0675:"top:avarage_topmost_contour_mid_point(closer)|bottom:avarage_extrema",                 #ٵ
0x0676:"top:topmost_contour_mid_point(closer)|bottom:bottommost_contour_mid_point",            #ٶ
0x0677:"top:mid|bottom:bottommost_contour_mid_point",                                          #ٷ
0x0678:"top:topmost_contour_mid_point(closer)|bottom:avarage_extrema",                         #ٸ
0x0679:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ٹ
0x067A:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ٺ
0x067B:"top:mid|bottom:bottommost_contour_mid_point",                                          #ٻ
0x067C:"top:topmost_contours_mid_point|bottom:bottommost_contour_mid_point",                   #ټ
0x067D:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ٽ
0x067E:"top:mid|bottom:avarage_bottommost_contour_mid_point",                                  #پ
0x067F:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ٿ
0x0680:"top:mid|bottom:bottommost_contours_mid_point",                                         #ڀ
0x0681:"top:topmost_contour_mid_point(closer)|bottom:avarage_extrema",                         #ځ
0x0682:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ڂ
0x0683:"top:mid|bottom:avarage_extrema",                                                       #ڃ
0x0684:"top:mid|bottom:avarage_extrema",                                                       #ڄ
0x0685:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #څ
0x0686:"top:mid|bottom:avarage_extrema",                                                       #چ
0x0687:"top:mid|bottom:avarage_extrema",                                                       #ڇ
0x0688:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ڈ
0x0689:"top:topmost_slope_mid|bottom:avarage_extrema",                                         #ډ
0x068A:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",                            #ڊ
0x068B:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",                    #ڋ
0x068C:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ڌ
0x068D:"top:topmost_slope_mid|bottom:bottommost_contours_mid_point",                           #ڍ
0x068E:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ڎ
0x068F:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ڏ
0x0690:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ڐ
0x0691:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",                    #ڑ
0x0692:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",                    #ڒ
0x0693:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",                            #ړ
0x0694:"top:topmost_slope_mid|bottom:avarage_bottommost_contour_mid_point",                    #ڔ
0x0695:"top:topmost_slope_mid|bottom:avarage_bottommost_contour_mid_point",                    #ڕ
0x0696:"top:topmost_slope_mid|bottom:avarage_bottommost_contour_mid_point",                    #ږ
0x0697:"top:topmost_contours_mid_point|bottom:bottommost_contour_mid_point",                   #ڗ
0x0698:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",                    #ژ
0x0699:"top:topmost_contours_mid_point|bottom:bottommost_contour_mid_point",                   #ڙ
0x069A:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ښ
0x069B:"top:BIG_y_extrema(after_x_bottom_extrema)|bottom:avarage_extrema",                     #ڛ
0x069C:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ڜ
0x069D:"top:avarage_extrema|bottom:avarage_extrema",                                           #ڝ
0x069E:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ڞ
0x069F:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ڟ
0x06A0:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ڠ
0x06A1:"top:avarage_extrema|bottom:avarage_extrema",                                           #ڡ
0x06A2:"top:avarage_extrema|bottom:bottommost_contour_mid_point",                              #ڢ
0x06A3:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contour_mid_point",            #ڣ
0x06A4:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ڤ
0x06A5:"top:avarage_extrema|bottom:bottommost_contour_mid_point",                              #ڥ
0x06A6:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ڦ
0x06A7:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ڧ
0x06A8:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ڨ
0x06A9:"top:kaf|bottom:avarage_extrema",                                                       #ک
0x06AA:"top:kaf|bottom:mid",                                                                   #ڪ
0x06AB:"top:kaf|bottom:avarage_extrema",                                                       #ګ
0x06AC:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ڬ
0x06AD:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ڭ
0x06AE:"top:avarage_topmost_contour_mid_point(closer)|bottom:bottommost_contour_mid_point",    #ڮ
0x06AF:"top:kaf|bottom:avarage_extrema",                                                       #گ
0x06B0:"top:kaf|bottom:avarage_extrema",                                                       #ڰ
0x06B1:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ڱ
0x06B2:"top:kaf|bottom:bottommost_contours_mid_point",                                         #ڲ
0x06B3:"top:kaf|bottom:bottommost_contour_mid_point",                                          #ڳ
0x06B4:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ڴ
0x06B5:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ڵ
0x06B6:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ڶ
0x06B7:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ڷ
0x06B8:"top:mid|bottom:bottommost_contour_mid_point",                                          #ڸ
0x06B9:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contour_mid_point",            #ڹ
0x06BA:"top:mid|bottom:avarage_extrema",                                                       #ں
0x06BB:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ڻ
0x06BC:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contour_mid_point",            #ڼ
0x06BD:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ڽ
0x06BE:"top:mid|bottom:mid",                                                                   #ھ
0x06BF:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ڿ
0x06C0:"top:topmost_contour_mid_point(closer)|bottom:avarage_extrema",                         #ۀ
0x06C1:"top:mid|bottom:avarage_extrema",                                                       #ہ
0x06C2:"top:topmost_contour_mid_point(closer)|bottom:avarage_extrema",                         #ۂ
0x06C3:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ۃ
0x06C4:"top:avarage_extrema|bottom:mid",                                                       #ۄ
0x06C5:"top:avarage_extrema|bottom:mid",                                                       #ۅ
0x06C6:"top:topmost_contour_mid_point|bottom:mid",                                             #ۆ
0x06C7:"top:topmost_contour_mid_point|bottom:mid",                                             #ۇ
0x06C8:"top:topmost_contour_mid_point|bottom:mid",                                             #ۈ
0x06C9:"top:topmost_contour_mid_point|bottom:mid",                                             #ۉ
0x06CA:"top:topmost_contours_mid_point|bottom:mid",                                            #ۊ
0x06CB:"top:topmost_contour_mid_point|bottom:mid",                                             #ۋ
0x06CC:"top:mid|bottom:avarage_extrema",                                                       #ی
0x06CD:"top:mid|bottom:avarage_extrema",                                                       #ۍ
0x06CE:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ێ
0x06CF:"top:topmost_contour_mid_point|bottom:mid",                                             #ۏ
0x06D0:"top:mid|bottom:bottommost_contour_mid_point",                                          #ې
0x06D1:"top:mid|bottom:bottommost_contour_mid_point",                                          #ۑ
0x06D2:"top:avarage_extrema|bottom:mid",                                                       #ے
0x06D3:"top:avarage_topmost_contour_mid_point(closer)|bottom:mid",                             #ۓ
0x06D5:"top:mid|bottom:avarage_extrema",                                                       #ە
0x06EE:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ۮ
0x06EF:"top:topmost_contour_mid_point|bottom:mid",                                             #ۯ
0x06FA:"top:avarage_topmost_contour_mid_point|bottom:avarage_bottommost_contour_mid_point",    #ۺ
0x06FB:"top:topmost_contour_mid_point|bottom:avarage_bottommost_contour_mid_point",            #ۻ
0x06FC:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ۼ
0x06FD:"top:avarage_extrema|bottom:bottommost_contours_mid_point",                             #۽
0x06FE:"top:avarage_extrema|bottom:mid",                                                       #۾
0x06FF:"top:topmost_contour_mid_point|bottom:mid",                                             #ۿ
0x0750:"top:mid|bottom:bottommost_contours_mid_point",                                         #ݐ
0x0751:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",                    #ݑ
0x0752:"top:mid|bottom:bottommost_contours_mid_point",                                         #ݒ
0x0753:"top:topmost_contours_mid_point|bottom:bottommost_contours_mid_point",                  #ݓ
0x0754:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contours_mid_point",           #ݔ
0x0755:"top:mid|bottom:bottommost_contour_mid_point",                                          #ݕ
0x0756:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ݖ
0x0757:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ݗ
0x0758:"top:mid|bottom:avarage_extrema",                                                       #ݘ
0x0759:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",                    #ݙ
0x075A:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",                            #ݚ
0x075B:"top:topmost_slope_mid|bottom:mid",                                                     #ݛ
0x075C:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ݜ
0x075D:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ݝ
0x075E:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ݞ
0x075F:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ݟ
0x0760:"top:avarage_extrema|bottom:bottommost_contours_mid_point",                             #ݠ
0x0761:"top:avarage_extrema|bottom:bottommost_contours_mid_point",                             #ݡ
0x0762:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ݢ
0x0763:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ݣ
0x0764:"top:kaf|bottom:bottommost_contours_mid_point",                                         #ݤ
0x0765:"top:topmost_contour_mid_point|bottom:avarage_extrema_ignore_left",                     #ݥ
0x0766:"top:avarage_extrema|bottom:avarage_bottommost_contour_mid_point",                      #ݦ
0x0767:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contours_mid_point",           #ݧ
0x0768:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ݨ
0x0769:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ݩ
0x076A:"top:mid|bottom:avarage_extrema",                                                       #ݪ
0x076B:"top:topmost_contour_mid_point|bottom:avarage_bottommost_contour_mid_point",            #ݫ
0x076C:"top:topmost_contour_mid_point(closer)|bottom:avarage_bottommost_contour_mid_point",    #ݬ
0x076D:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ݭ
0x076E:"top:mid|bottom:avarage_extrema",                                                       #ݮ
0x076F:"top:mid|bottom:avarage_extrema",                                                       #ݯ
0x0770:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ݰ
0x0771:"top:topmost_contour_mid_point|bottom:avarage_bottommost_contour_mid_point",            #ݱ
0x0772:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ݲ
0x0773:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ݳ
0x0774:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ݴ
0x0775:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ݵ
0x0776:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ݶ
0x0777:"top:mid|bottom:bottommost_contour_mid_point",                                          #ݷ
0x0778:"top:avarage_topmost_contour_mid_point|bottom:avarage_bottommost_contour_mid_point",    #ݸ
0x0779:"top:avarage_topmost_contour_mid_point|bottom:avarage_bottommost_contour_mid_point",    #ݹ
0x077A:"top:avarage_topmost_contour_mid_point|bottom:mid",                                     #ݺ
0x077B:"top:avarage_topmost_contour_mid_point|bottom:mid",                                     #ݻ
0x077C:"top:mid|bottom:avarage_extrema",                                                       #ݼ
0x077D:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ݽ
0x077E:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ݾ
0x077F:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ݿ
0x08A0:"top:mid|bottom:bottommost_contour_mid_point",                                          #ࢠ
0x08A1:"top:avarage_topmost_contour_mid_point(closer)|bottom:bottommost_contour_mid_point",    #ࢡ
0x08A2:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ࢢ
0x08A3:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ࢣ
0x08A4:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",                    #ࢤ
0x08A5:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ࢥ
0x08A6:"top:mid|bottom:avarage_extrema",                                                       #ࢦ
0x08A7:"top:topmost_contour_mid_point|bottom:avarage_extrema_ignore_left",                     #ࢧ
0x08A8:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contours_mid_point",           #ࢨ
0x08A9:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contours_mid_point",           #ࢩ
0x08AA:"top:topmost_slope_mid|bottom:avarage_extrema",                                         #ࢪ
0x08AB:"top:avarage_extrema|bottom:mid",                                                       #ࢫ
0x08AC:"top:avarage_extrema|bottom:bottommost_contours_mid_point",                             #ࢬ
0x08AE:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",                            #ࢮ
0x08AF:"top:avarage_extrema|bottom:bottommost_contour_mid_point",                              #ࢯ
0x08B0:"top:kaf|bottom:avarage_extrema",                                                       #ࢰ
0x08B1:"top:avarage_extrema|bottom:avarage_extrema",                                           #ࢱ
0x08B2:"top:topmost_contour_mid_point|bottom:mid",                                             #ࢲ
0x08B3:"top:avarage_extrema|bottom:avarage_extrema",                                           #ࢳ
0x08B4:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contour_mid_point",            #ࢴ
0x08B6:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contour_mid_point",            #ࢶ
0x08B7:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contour_mid_point",            #ࢷ
0x08B8:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ࢸ
0x08B9:"top:avarage_topmost_contour_mid_point|bottom:mid",                                     #ࢹ
0x08BA:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contours_mid_point",           #ࢺ
0x08BB:"top:avarage_extrema|bottom:avarage_extrema",                                           #ࢻ
0x08BC:"top:avarage_extrema|bottom:avarage_extrema",                                           #ࢼ
0x08BD:"top:mid|bottom:avarage_extrema",                                                       #ࢽ
#-----------------------------------------------
0xFB50:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﭐ
0xFB51:"top:topmost_contour_mid_point|bottom:mid",                                             #ﭑ
0xFB52:"top:mid|bottom:bottommost_contour_mid_point",                                          #ﭒ
0xFB53:"top:mid|bottom:bottommost_contour_mid_point",                                          #ﭓ
0xFB54:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",                            #ﭔ
0xFB55:"top:avarage_extrema|bottom:bottommost_contour_mid_point",                              #ﭕ
0xFB56:"top:mid|bottom:bottommost_contour_mid_point",                                          #ﭖ
0xFB57:"top:mid|bottom:bottommost_contour_mid_point",                                          #ﭗ
0xFB58:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",                            #ﭘ
0xFB59:"top:avarage_extrema|bottom:bottommost_contour_mid_point",                              #ﭙ
0xFB5A:"top:mid|bottom:bottommost_contours_mid_point",                                         #ﭚ
0xFB5B:"top:mid|bottom:bottommost_contours_mid_point",                                         #ﭛ
0xFB5C:"top:topmost_slope_mid|bottom:bottommost_contours_mid_point",                           #ﭜ
0xFB5D:"top:avarage_extrema|bottom:bottommost_contours_mid_point",                             #ﭝ
0xFB5E:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﭞ
0xFB5F:"top:topmost_contour_mid_point|bottom:avarage_extrema_center",                          #ﭟ
0xFB60:"top:topmost_contour_mid_point|bottom:mid",                                             #ﭠ
0xFB61:"top:topmost_contour_mid_point|bottom:mid",                                             #ﭡ
0xFB62:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ﭢ
0xFB63:"top:topmost_contours_mid_point|bottom:avarage_extrema_center",                         #ﭣ
0xFB64:"top:topmost_contours_mid_point|bottom:mid",                                            #ﭤ
0xFB65:"top:topmost_contours_mid_point|bottom:mid",                                            #ﭥ
0xFB66:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﭦ
0xFB67:"top:topmost_contour_mid_point|bottom:avarage_extrema_center",                          #ﭧ
0xFB68:"top:topmost_contour_mid_point|bottom:mid",                                             #ﭨ
0xFB69:"top:topmost_contour_mid_point|bottom:mid",                                             #ﭩ
0xFB6A:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ﭪ
0xFB6B:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema_center",                  #ﭫ
0xFB6C:"top:topmost_contour_mid_point|bottom:mid",                                             #ﭬ
0xFB6D:"top:topmost_contour_mid_point|bottom:mid",                                             #ﭭ
0xFB6E:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ﭮ
0xFB6F:"top:topmost_contours_mid_point|bottom:avarage_extrema_center",                         #ﭯ
0xFB70:"top:topmost_contours_mid_point|bottom:mid",                                            #ﭰ
0xFB71:"top:topmost_contours_mid_point|bottom:mid",                                            #ﭱ
0xFB72:"top:mid|bottom:avarage_extrema",                                                       #ﭲ
0xFB73:"top:mid|bottom:avarage_extrema",                                                       #ﭳ
0xFB74:"top:avarage_extrema|bottom:bottommost_contour_mid_point",                              #ﭴ
0xFB75:"top:avarage_extrema|bottom:bottommost_contour_mid_point",                              #ﭵ
0xFB76:"top:mid|bottom:avarage_extrema",                                                       #ﭶ
0xFB77:"top:mid|bottom:avarage_extrema",                                                       #ﭷ
0xFB78:"top:avarage_extrema|bottom:bottommost_contours_mid_point",                             #ﭸ
0xFB79:"top:avarage_extrema|bottom:bottommost_contours_mid_point",                             #ﭹ
0xFB7A:"top:mid|bottom:avarage_extrema",                                                       #ﭺ
0xFB7B:"top:mid|bottom:avarage_extrema",                                                       #ﭻ
0xFB7C:"top:avarage_extrema|bottom:bottommost_contour_mid_point",                              #ﭼ
0xFB7D:"top:avarage_extrema|bottom:bottommost_contour_mid_point",                              #ﭽ
0xFB7E:"top:mid|bottom:avarage_extrema",                                                       #ﭾ
0xFB7F:"top:mid|bottom:avarage_extrema",                                                       #ﭿ
0xFB80:"top:avarage_extrema|bottom:bottommost_contours_mid_point",                             #ﮀ
0xFB81:"top:avarage_extrema|bottom:bottommost_contours_mid_point",                             #ﮁ
0xFB82:"top:topmost_slope_mid|bottom:bottommost_contours_mid_point",                           #ﮂ
0xFB83:"top:topmost_slope_mid|bottom:bottommost_contours_mid_point",                           #ﮃ
0xFB84:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ﮄ
0xFB85:"top:topmost_contours_mid_point|bottom:avarage_extrema_center",                         #ﮅ
0xFB86:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﮆ
0xFB87:"top:topmost_contour_mid_point|bottom:avarage_extrema_center",                          #ﮇ
0xFB88:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﮈ
0xFB89:"top:topmost_contour_mid_point|bottom:avarage_extrema_center",                          #ﮉ
0xFB8A:"top:topmost_contour_mid_point|bottom:mid",                                             #ﮊ
0xFB8B:"top:topmost_contour_mid_point|bottom:mid",                                             #ﮋ
0xFB8C:"top:topmost_contour_mid_point|bottom:mid",                                             #ﮌ
0xFB8D:"top:topmost_contour_mid_point|bottom:mid",                                             #ﮍ
0xFB8E:"top:kaf|bottom:avarage_extrema",                                                       #ﮎ
0xFB8F:"top:kaf|bottom:avarage_extrema_center",                                                #ﮏ
0xFB90:"top:kaf|bottom:mid",                                                                   #ﮐ
0xFB91:"top:kaf|bottom:mid",                                                                   #ﮑ
0xFB92:"top:kaf|bottom:avarage_extrema",                                                       #ﮒ
0xFB93:"top:kaf|bottom:avarage_extrema_center",                                                #ﮓ
0xFB94:"top:kaf|bottom:mid",                                                                   #ﮔ
0xFB95:"top:kaf|bottom:mid",                                                                   #ﮕ
0xFB96:"top:kaf|bottom:bottommost_contour_mid_point",                                          #ﮖ
0xFB97:"top:kaf|bottom:bottommost_contour_mid_point",                                          #ﮗ
0xFB98:"top:kaf|bottom:bottommost_contour_mid_point",                                          #ﮘ
0xFB99:"top:kaf|bottom:bottommost_contour_mid_point",                                          #ﮙ
0xFB9A:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ﮚ
0xFB9B:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema_center",                  #ﮛ
0xFB9C:"top:avarage_topmost_contour_mid_point|bottom:mid",                                     #ﮜ
0xFB9D:"top:avarage_topmost_contour_mid_point|bottom:mid",                                     #ﮝ
0xFB9E:"top:mid|bottom:avarage_extrema",                                                       #ﮞ
0xFB9F:"top:mid|bottom:avarage_extrema",                                                       #ﮟ
0xFBA0:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ﮠ
0xFBA1:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ﮡ
0xFBA2:"top:avarage_topmost_contour_mid_point|bottom:mid",                                     #ﮢ
0xFBA3:"top:avarage_topmost_contour_mid_point|bottom:mid",                                     #ﮣ
0xFBA4:"top:topmost_contour_mid_point(closer)|bottom:avarage_extrema",                         #ﮤ
0xFBA5:"top:topmost_contour_mid_point(closer)|bottom:mid",                                     #ﮥ
0xFBA6:"top:mid|bottom:avarage_extrema",                                                       #ﮦ
0xFBA7:"top:avarage_extrema|bottom:mid",                                                       #ﮧ
0xFBA8:"top:topmost_slope_mid|bottom:avarage_extrema",                                         #ﮨ
0xFBA9:"top:mid|bottom:avarage_extrema",                                                       #ﮩ
0xFBAA:"top:mid|bottom:mid",                                                                   #ﮪ
0xFBAB:"top:mid|bottom:mid",                                                                   #ﮫ
0xFBAC:"top:mid|bottom:mid",                                                                   #ﮬ
0xFBAD:"top:mid|bottom:avarage_extrema",                                                       #ﮭ
0xFBAE:"top:mid|bottom:mid",                                                                   #ﮮ
0xFBAF:"top:mid|bottom:mid",                                                                   #ﮯ
0xFBB0:"top:topmost_contour_mid_point(closer)|bottom:mid",                                     #ﮰ
0xFBB1:"top:topmost_contour_mid_point(closer)|bottom:mid",                                     #ﮱ
-----------------------------------------------
0xFBD3:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ﯓ
0xFBD4:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema_center",                  #ﯔ
0xFBD5:"top:avarage_topmost_contour_mid_point|bottom:mid",                                     #ﯕ
0xFBD6:"top:avarage_topmost_contour_mid_point|bottom:mid",                                     #ﯖ
0xFBD7:"top:topmost_contour_mid_point|bottom:mid",                                             #ﯗ
0xFBD8:"top:topmost_contour_mid_point|bottom:mid",                                             #ﯘ
0xFBD9:"top:topmost_contour_mid_point|bottom:mid",                                             #ﯙ
0xFBDA:"top:topmost_contour_mid_point|bottom:mid",                                             #ﯚ
0xFBDB:"top:topmost_contour_mid_point|bottom:mid",                                             #ﯛ
0xFBDC:"top:topmost_contour_mid_point|bottom:mid",                                             #ﯜ
0xFBDD:"top:mid|bottom:mid",                                                                   #ﯝ
0xFBDE:"top:topmost_contour_mid_point|bottom:mid",                                             #ﯞ
0xFBDF:"top:topmost_contour_mid_point|bottom:mid",                                             #ﯟ
0xFBE0:"top:avarage_extrema|bottom:mid",                                                       #ﯠ
0xFBE1:"top:avarage_extrema|bottom:mid",                                                       #ﯡ
0xFBE3:"top:topmost_contour_mid_point|bottom:mid",                                             #ﯣ
0xFBE4:"top:mid|bottom:bottommost_contour_mid_point",                                          #ﯤ
0xFBE5:"top:mid|bottom:bottommost_contour_mid_point",                                          #ﯥ
0xFBE6:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",                            #ﯦ
0xFBE7:"top:avarage_extrema|bottom:bottommost_contour_mid_point",                              #ﯧ
0xFBE8:"top:topmost_slope_mid|bottom:mid",                                                     #ﯨ
0xFBE9:"top:avarage_extrema|bottom:mid",                                                       #ﯩ
#-----------------------------------------------
0xFBFC:"top:mid|bottom:avarage_extrema",                                                       #ﯼ
0xFBFD:"top:mid|bottom:avarage_extrema",                                                       #ﯽ
0xFBFE:"top:topmost_slope_mid|bottom:bottommost_contours_mid_point",                           #ﯾ
0xFBFF:"top:avarage_extrema|bottom:bottommost_contours_mid_point",                             #ﯿ
#-----------------------------------------------
0xFCF2:"top:topmost_contour_mid_point|bottom:mid",                                             #ﳲ
0xFCF3:"top:topmost_contour_mid_point|bottom:mid",                                             #ﳳ
0xFCF4:"top:topmost_contour_mid_point|bottom:mid",                                             #ﳴ
0xFD3C:"top:topmost_contour_mid_point|bottom:mid",                                             #ﴼ
0xFD3D:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﴽ
#-----------------------------------------------
0xFE70:"top:mid|bottom:mid",                                                                   #ﹰ
0xFE71:"top:topmost_contour_mid_point|bottom:mid",                                             #ﹱ
0xFE72:"top:mid|bottom:mid",                                                                   #ﹲ
0xFE73:"top:mid|bottom:mid",                                                                   #ﹳ
0xFE74:"top:mid|bottom:mid",                                                                   #ﹴ
#-----------------------------------------------
0xFE76:"top:mid|bottom:mid",                                                                   #ﹶ
0xFE77:"top:topmost_contour_mid_point|bottom:mid",                                             #ﹷ
0xFE78:"top:mid|bottom:mid",                                                                   #ﹸ
0xFE79:"top:topmost_contour_mid_point|bottom:mid",                                             #ﹹ
0xFE7A:"top:mid|bottom:mid",                                                                   #ﹺ
0xFE7B:"top:mid|bottom:bottommost_contour_mid_point",                                          #ﹻ
0xFE7C:"top:mid|bottom:mid",                                                                   #ﹼ
0xFE7D:"top:topmost_contour_mid_point|bottom:mid",                                             #ﹽ
0xFE7E:"top:mid|bottom:mid",                                                                   #ﹾ
0xFE7F:"top:topmost_contour_mid_point|bottom:mid",                                             #ﹿ
0xFE80:"top:avarage_extrema|bottom:mid",                                                       #ﺀ
0xFE81:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﺁ
0xFE82:"top:topmost_contour_mid_point|bottom:mid",                                             #ﺂ
0xFE83:"top:topmost_contour_mid_point(closer)|bottom:avarage_extrema",                         #ﺃ
0xFE84:"top:topmost_contour_mid_point(closer)|bottom:mid",                                     #ﺄ
0xFE85:"top:topmost_contour_mid_point(closer)|bottom:mid",                                     #ﺅ
0xFE86:"top:topmost_contour_mid_point(closer)|bottom:mid",                                     #ﺆ
0xFE87:"top:avarage_extrema|bottom:bottommost_contour_mid_point(closer)",                      #ﺇ
0xFE88:"top:avarage_extrema|bottom:bottommost_contour_mid_point(closer)",                      #ﺈ
0xFE89:"top:topmost_contour_mid_point(closer)|bottom:avarage_extrema",                         #ﺉ
0xFE8A:"top:topmost_contour_mid_point(closer)|bottom:avarage_extrema",                         #ﺊ
0xFE8B:"top:topmost_contour_mid_point(closer)|bottom:mid",                                     #ﺋ
0xFE8C:"top:topmost_contour_mid_point(closer)|bottom:mid",                                     #ﺌ
0xFE8D:"top:avarage_extrema|bottom:avarage_extrema",                                           #ﺍ
0xFE8E:"top:avarage_extrema|bottom:mid",                                                       #ﺎ
0xFE8F:"top:mid|bottom:bottommost_contour_mid_point",                                          #ﺏ
0xFE90:"top:mid|bottom:bottommost_contour_mid_point",                                          #ﺐ
0xFE91:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",                            #ﺑ
0xFE92:"top:avarage_extrema|bottom:bottommost_contour_mid_point",                              #ﺒ
0xFE93:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ﺓ
0xFE94:"top:topmost_contours_mid_point|bottom:mid",                                            #ﺔ
0xFE95:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ﺕ
0xFE96:"top:topmost_contours_mid_point|bottom:avarage_extrema_center",                         #ﺖ
0xFE97:"top:topmost_contours_mid_point|bottom:mid",                                            #ﺗ
0xFE98:"top:topmost_contours_mid_point|bottom:mid",                                            #ﺘ
0xFE99:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﺙ
0xFE9A:"top:topmost_contour_mid_point|bottom:avarage_extrema_center",                          #ﺚ
0xFE9B:"top:topmost_contour_mid_point|bottom:mid",                                             #ﺛ
0xFE9C:"top:topmost_contour_mid_point|bottom:mid",                                             #ﺜ
0xFE9D:"top:mid|bottom:avarage_extrema",                                                       #ﺝ
0xFE9E:"top:mid|bottom:avarage_extrema",                                                       #ﺞ
0xFE9F:"top:avarage_extrema|bottom:bottommost_contour_mid_point",                              #ﺟ
0xFEA0:"top:avarage_extrema|bottom:bottommost_contour_mid_point",                              #ﺠ
0xFEA1:"top:mid|bottom:avarage_extrema",                                                       #ﺡ
0xFEA2:"top:mid|bottom:avarage_extrema",                                                       #ﺢ
0xFEA3:"top:avarage_extrema|bottom:mid",                                                       #ﺣ
0xFEA4:"top:avarage_extrema|bottom:mid",                                                       #ﺤ
0xFEA5:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﺥ
0xFEA6:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﺦ
0xFEA7:"top:topmost_contour_mid_point|bottom:mid",                                             #ﺧ
0xFEA8:"top:topmost_contour_mid_point|bottom:mid",                                             #ﺨ
0xFEA9:"top:topmost_slope_mid|bottom:avarage_extrema",                                         #ﺩ
0xFEAA:"top:topmost_slope_mid|bottom:avarage_extrema_center",                                  #ﺪ
0xFEAB:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﺫ
0xFEAC:"top:topmost_contour_mid_point|bottom:avarage_extrema_center",                          #ﺬ
0xFEAD:"top:topmost_slope_mid|bottom:mid",                                                     #ﺭ
0xFEAE:"top:topmost_slope_mid|bottom:mid",                                                     #ﺮ
0xFEAF:"top:topmost_contour_mid_point|bottom:mid",                                             #ﺯ
0xFEB0:"top:topmost_contour_mid_point|bottom:mid",                                             #ﺰ
0xFEB1:"top:BIG_y_extrema(after_x_bottom_extrema)|bottom:avarage_extrema",                     #ﺱ
0xFEB2:"top:BIG_y_extrema(after_x_bottom_extrema)|bottom:avarage_extrema",                     #ﺲ
0xFEB3:"top:BIG_y_extrema|bottom:mid",                                                         #ﺳ
0xFEB4:"top:BIG_y_extrema|bottom:mid",                                                         #ﺴ
0xFEB5:"top:topmost_contour_mid_point|bottom:exrtema",                                         #ﺵ
0xFEB6:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﺶ
0xFEB7:"top:topmost_contour_mid_point|bottom:mid",                                             #ﺷ
0xFEB8:"top:topmost_contour_mid_point|bottom:mid",                                             #ﺸ
0xFEB9:"top:avarage_extrema|bottom:avarage_extrema",                                           #ﺹ
0xFEBA:"top:avarage_extrema|bottom:avarage_extrema",                                           #ﺺ
0xFEBB:"top:avarage_extrema|bottom:mid",                                                       #ﺻ
0xFEBC:"top:avarage_extrema|bottom:mid",                                                       #ﺼ
0xFEBD:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﺽ
0xFEBE:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﺾ
0xFEBF:"top:topmost_contour_mid_point|bottom:mid",                                             #ﺿ
0xFEC0:"top:topmost_contour_mid_point|bottom:mid",                                             #ﻀ
0xFEC1:"top:avarage_extrema_ignore_left|bottom:mid",                                           #ﻁ
0xFEC2:"top:avarage_extrema_ignore_left|bottom:mid",                                           #ﻂ
0xFEC3:"top:avarage_extrema_ignore_left|bottom:mid",                                           #ﻃ
0xFEC4:"top:avarage_extrema_ignore_left|bottom:mid",                                           #ﻄ
0xFEC5:"top:avarage_topmost_contour_mid_point|bottom:mid",                                     #ﻅ
0xFEC6:"top:avarage_topmost_contour_mid_point|bottom:mid",                                     #ﻆ
0xFEC7:"top:avarage_topmost_contour_mid_point|bottom:mid",                                     #ﻇ
0xFEC8:"top:avarage_topmost_contour_mid_point|bottom:mid",                                     #ﻈ
0xFEC9:"top:avarage_extrema|bottom:avarage_extrema",                                           #ﻉ
0xFECA:"top:avarage_extrema|bottom:avarage_extrema",                                           #ﻊ
0xFECB:"top:avarage_extrema|bottom:mid",                                                       #ﻋ
0xFECC:"top:avarage_extrema|bottom:mid",                                                       #ﻌ
0xFECD:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﻍ
0xFECE:"top:topmost_contour_mid_point|bottom:avarage_extrema",                                 #ﻎ
0xFECF:"top:topmost_contour_mid_point|bottom:mid",                                             #ﻏ
0xFED0:"top:topmost_contour_mid_point|bottom:mid",                                             #ﻐ
0xFED1:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ﻑ
0xFED2:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema_center",                  #ﻒ
0xFED3:"top:topmost_contour_mid_point|bottom:mid",                                             #ﻓ
0xFED4:"top:topmost_contour_mid_point|bottom:mid",                                             #ﻔ
0xFED5:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ﻕ
0xFED6:"top:topmost_contours_mid_point|bottom:avarage_extrema",                                #ﻖ
0xFED7:"top:topmost_contours_mid_point|bottom:mid",                                            #ﻗ
0xFED8:"top:topmost_contours_mid_point|bottom:mid",                                            #ﻘ
0xFED9:"top:avarage_topmost_contour_mid_point(closer)|bottom:avarage_extrema",                 #ﻙ
0xFEDA:"top:avarage_topmost_contour_mid_point(closer)|bottom:avarage_extrema_center",          #ﻚ
0xFEDB:"top:kaf|bottom:mid",                                                                   #ﻛ
0xFEDC:"top:kaf|bottom:mid",                                                                   #ﻜ
0xFEDD:"top:mid|bottom:avarage_extrema",                                                       #ﻝ
0xFEDE:"top:mid|bottom:avarage_extrema",                                                       #ﻞ
0xFEDF:"top:avarage_extrema|bottom:mid",                                                       #ﻟ
0xFEE0:"top:avarage_extrema|bottom:mid",                                                       #ﻠ
0xFEE1:"top:avarage_extrema|bottom:avarage_extrema_ignore_left",                               #ﻡ
0xFEE2:"top:avarage_extrema|bottom:avarage_extrema_ignore_left_center",                        #ﻢ
0xFEE3:"top:avarage_extrema|bottom:avarage_extrema_center",                                    #ﻣ
0xFEE4:"top:avarage_extrema|bottom:avarage_extrema_center",                                    #ﻤ
0xFEE5:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ﻥ
0xFEE6:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",                         #ﻦ
0xFEE7:"top:topmost_contour_mid_point|bottom:mid",                                             #ﻧ
0xFEE8:"top:topmost_contour_mid_point|bottom:mid",                                             #ﻨ
0xFEE9:"top:mid|bottom:avarage_extrema",                                                       #ﻩ
0xFEEA:"top:mid|bottom:mid",                                                                   #ﻪ
0xFEEB:"top:mid|bottom:mid",                                                                   #ﻫ
0xFEEC:"top:avarage_extrema|bottom:avarage_extrema",                                           #ﻬ
0xFEED:"top:avarage_extrema|bottom:mid",                                                       #ﻭ
0xFEEE:"top:avarage_extrema|bottom:mid",                                                       #ﻮ
0xFEEF:"top:mid|bottom:avarage_extrema",                                                       #ﻯ
0xFEF0:"top:mid|bottom:avarage_extrema",                                                       #ﻰ
0xFEF1:"top:mid|bottom:bottommost_contours_mid_point",                                         #ﻱ
0xFEF2:"top:mid|bottom:bottommost_contours_mid_point",                                         #ﻲ
0xFEF3:"top:topmost_slope_mid|bottom:bottommost_contours_mid_point",                           #ﻳ
0xFEF4:"top:avarage_extrema|bottom:bottommost_contours_mid_point"                              #ﻴ
}
non_Unicode_base_glyphs_dict_fina ={
0x0620:"top:mid|bottom:bottommost_contour_mid_point",
0x063B:"top:topmost_contour_mid_point|bottom:avarage_extrema_center",
0x063C:"top:kaf|bottom:bottommost_contour_mid_point",
0x063D:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x063E:"top:topmost_contours_mid_point|bottom:avarage_extrema_center",
0x063F:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x066E:"top:mid|bottom:avarage_extrema_center",
0x066F:"top:avarage_extrema|bottom:avarage_extrema",
0x0672:"top:topmost_contour_mid_point(closer)|bottom:mid",
0x0673:"top:avarage_extrema|bottom:bottommost_contour_mid_point(closer)",
0x0675:"top:avarage_topmost_contour_mid_point(closer)|bottom:mid",
0x0676:"top:topmost_contour_mid_point(closer)|bottom:mid",
0x0677:"top:mid|bottom:mid",
0x0678:"top:avarage_topmost_contour_mid_point(closer)|bottom:avarage_extrema",
0x067C:"top:topmost_contours_mid_point|bottom:bottommost_contour_mid_point",
0x067D:"top:topmost_contours_mid_point|bottom:avarage_extrema_center",
0x0681:"top:topmost_contour_mid_point(closer)|bottom:avarage_extrema",
0x0682:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x0685:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x0689:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",
0x068A:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",
0x068B:"top:topmost_contour_mid_point|bottom:topmost_contour_mid_point",
0x068F:"top:topmost_contours_mid_point|bottom:avarage_extrema_center",
0x0690:"top:topmost_contours_mid_point|bottom:avarage_extrema_center",
0x0692:"top:topmost_contour_mid_point|bottom:mid",
0x0693:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",
0x0694:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",
0x0695:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",
0x0696:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",
0x0697:"top:topmost_contours_mid_point|bottom:mid",
0x0699:"top:topmost_contours_mid_point|bottom:mid",
0x069A:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x069B:"top:BIG_y_extrema(after_x_bottom_extrema)|bottom:bottommost_contour_mid_point",
0x069C:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x069D:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x069E:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x069F:"top:avarage_topmost_contour_mid_point|bottom:mid",
0x06A0:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x06A1:"top:avarage_extrema|bottom:avarage_extrema_center",
0x06A2:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x06A3:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06A5:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x06A7:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x06A8:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x06AA:"top:kaf|bottom:mid",
0x06AB:"top:kaf|bottom:avarage_extrema_center",
0x06AC:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema_center",
0x06AE:"top:avarage_topmost_contour_mid_point(closer)|bottom:bottommost_contour_mid_point",
0x06B0:"top:kaf|bottom:avarage_extrema_center",
0x06B2:"top:kaf|bottom:bottommost_contour_mid_point",
0x06B4:"top:topmost_contour_mid_point|bottom:avarage_extrema_center",
0x06B5:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x06B6:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x06B7:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x06B8:"top:mid|bottom:avarage_extrema",
0x06B9:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06BC:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06BD:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",
0x06BF:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x06C4:"top:avarage_extrema|bottom:mid",
0x06CA:"top:topmost_contours_mid_point|bottom:mid",
0x06CD:"top:mid|bottom:avarage_extrema",
0x06CE:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x06CF:"top:topmost_contour_mid_point|bottom:mid",
0x06D1:"top:mid|bottom:bottommost_contour_mid_point",
0x06EE:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x06EF:"top:topmost_contour_mid_point|bottom:mid",
0x06FA:"top:topmost_contour_mid_point|bottom:avarage_bottommost_contour_mid_point",
0x06FB:"top:topmost_contour_mid_point|bottom:avarage_bottommost_contour_mid_point",
0x06FC:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x06FF:"top:topmost_contour_mid_point|bottom:mid",
0x0750:"top:mid|bottom:bottommost_contours_mid_point",
0x0751:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x0752:"top:mid|bottom:bottommost_contour_mid_point",
0x0753:"top:topmost_contours_mid_point|bottom:bottommost_contour_mid_point",
0x0754:"top:topmost_contours_mid_point|bottom:bottommost_contour_mid_point",
0x0755:"top:mid|bottom:bottommost_contour_mid_point",
0x0756:"top:topmost_contours_mid_point|bottom:avarage_extrema_center",
0x0757:"top:topmost_contours_mid_point|bottom:avarage_extrema",
0x0758:"top:mid|bottom:avarage_extrema",
0x0759:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x075A:"top:topmost_slope_mid|bottom:bottommost_contour_mid_point",
0x075B:"top:topmost_slope_mid|bottom:mid",
0x075C:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x075D:"top:topmost_contours_mid_point|bottom:avarage_extrema",
0x075E:"top:topmost_contours_mid_point|bottom:avarage_extrema",
0x075F:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x0760:"top:avarage_extrema|bottom:bottommost_contours_mid_point",
0x0761:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x0762:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema_center",
0x0763:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema_center",
0x0764:"top:kaf|bottom:bottommost_contours_mid_point",
0x0765:"top:topmost_contour_mid_point|bottom:avarage_extrema_ignore_left_center",
0x0766:"top:avarage_extrema|bottom:avarage_bottommost_contour_mid_point",
0x0767:"top:avarage_topmost_contour_mid_point|bottom:avarage_extrema",
0x0768:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x0769:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x076A:"top:mid|bottom:avarage_extrema",
0x076B:"top:topmost_contour_mid_point|bottom:mid",
0x076C:"top:topmost_contour_mid_point(closer)|bottom:mid",
0x076D:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x076E:"top:mid|bottom:avarage_extrema",
0x076F:"top:mid|bottom:avarage_extrema",
0x0770:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x0771:"top:topmost_contour_mid_point|bottom:mid",
0x0772:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x0773:"top:topmost_contour_mid_point|bottom:mid",
0x0774:"top:topmost_contour_mid_point|bottom:mid",
0x0775:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x0776:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x0777:"top:mid|bottom:bottommost_contour_mid_point",
0x0778:"top:topmost_contour_mid_point|bottom:mid",
0x0779:"top:topmost_contour_mid_point|bottom:mid",
0x077A:"top:topmost_contour_mid_point|bottom:mid",
0x077B:"top:topmost_contour_mid_point|bottom:mid",
0x077C:"top:mid|bottom:avarage_extrema",
0x077D:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x077E:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x077F:"top:topmost_contours_mid_point|bottom:avarage_extrema_center",
0x08A0:"top:mid|bottom:bottommost_contour_mid_point",
0x08A1:"top:topmost_contour_mid_point(closer)|bottom:bottommost_contour_mid_point",
0x08A2:"top:topmost_contours_mid_point|bottom:avarage_extrema",
0x08A3:"top:topmost_contours_mid_point|bottom:mid",
0x08A4:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x08A5:"top:topmost_contours_mid_point|bottom:bottommost_contour_mid_point",
0x08A6:"top:mid|bottom:avarage_extrema",
0x08A7:"top:topmost_contour_mid_point|bottom:avarage_extrema_ignore_left_center",
0x08A8:"top:topmost_contour_mid_point(closer)|bottom:bottommost_contours_mid_point",
0x08A9:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contours_mid_point",
0x08AA:"top:topmost_slope_mid|bottom:avarage_extrema",
0x08AB:"top:avarage_extrema|bottom:mid",
0x08AC:"top:avarage_extrema|bottom:bottommost_contours_mid_point",
0x08AE:"top:topmost_slope_mid|bottom:bottommost_contours_mid_point",
0x08AF:"top:avarage_extrema|bottom:bottommost_contours_mid_point",
0x08B0:"top:kaf|bottom:avarage_extrema_center",
0x08B1:"top:avarage_extrema|bottom:avarage_extrema",
0x08B2:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x08B3:"top:avarage_extrema|bottom:avarage_extrema",
0x08B4:"top:avarage_topmost_contour_mid_point(closer)|bottom:bottommost_contour_mid_point",
0x08B9:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contour_mid_point"
}
non_Unicode_base_glyphs_dict_medi ={
0x0620:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x063B:"top:topmost_contour_mid_point|bottom:mid",
0x063C:"top:kaf|bottom:bottommost_contour_mid_point",
0x063D:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contours_mid_point",
0x063E:"top:topmost_contours_mid_point|bottom:bottommost_contours_mid_point",
0x063F:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contours_mid_point",
0x066F:"top:avarage_extrema|bottom:avarage_extrema",
0x067C:"top:topmost_contours_mid_point|bottom:avarage_bottommost_contour_mid_point",
0x067D:"top:topmost_contours_mid_point|bottom:mid",
0x0681:"top:topmost_contour_mid_point(closer)|bottom:mid",
0x0682:"top:topmost_contour_mid_point|bottom:mid",
0x0685:"top:topmost_contour_mid_point|bottom:mid",
0x069A:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x069B:"top:BIG_y_extrema|bottom:avarage_extrema",
0x069C:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x069D:"top:avarage_extrema|bottom:bottommost_contours_mid_point",
0x069E:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x06A0:"top:topmost_contour_mid_point|bottom:mid",
0x06A1:"top:avarage_extrema|bottom:mid",
0x06A2:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x06A3:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06A5:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x06AA:"top:kaf|bottom:mid",
0x06AB:"top:kaf|bottom:mid",
0x06AC:"top:topmost_contour_mid_point|bottom:mid",
0x06AE:"top:kaf|bottom:bottommost_contour_mid_point",
0x06B0:"top:kaf|bottom:mid",
0x06B2:"top:kaf|bottom:bottommost_contours_mid_point",
0x06B4:"top:topmost_contour_mid_point|bottom:mid",
0x06B5:"top:topmost_contour_mid_point|bottom:mid",
0x06B6:"top:topmost_contour_mid_point|bottom:mid",
0x06B7:"top:topmost_contour_mid_point|bottom:mid",
0x06B8:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x06B9:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06BC:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06BF:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06CE:"top:topmost_contour_mid_point|bottom:bottommost_contours_mid_point",
0x06FA:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06FB:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06FC:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06FF:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x0750:"top:avarage_extrema|bottom:bottommost_contours_mid_point",
0x0751:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x0752:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x0753:"top:topmost_contours_mid_point|bottom:bottommost_contours_mid_point",
0x0754:"top:topmost_contour_mid_point|bottom:bottommost_contours_mid_point",
0x0755:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x0756:"top:topmost_contour_mid_point|bottom:mid",
0x0757:"top:topmost_contours_mid_point|bottom:mid",
0x0758:"top:avarage_extrema|bottom:bottommost_contours_mid_point",
0x075C:"top:topmost_contours_mid_point|bottom:mid",
0x075D:"top:topmost_contours_mid_point|bottom:mid",
0x075E:"top:topmost_contours_mid_point|bottom:mid",
0x075F:"top:topmost_contour_mid_point|bottom:mid",
0x0760:"top:avarage_extrema|bottom:bottommost_contours_mid_point",
0x0761:"top:avarage_extrema|bottom:bottommost_contours_mid_point",
0x0762:"top:avarage_topmost_contour_mid_point|bottom:mid",
0x0763:"top:topmost_contour_mid_point|bottom:mid",
0x0764:"top:kaf|bottom:bottommost_contours_mid_point",
0x0765:"top:topmost_contour_mid_point|bottom:avarage_extrema_center",
0x0766:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x0768:"top:topmost_contour_mid_point|bottom:mid",
0x0769:"top:topmost_contour_mid_point|bottom:mid",
0x076A:"top:avarage_extrema|bottom:mid",
0x076D:"top:topmost_contour_mid_point|bottom:mid",
0x076E:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x076F:"top:topmost_contour_mid_point|bottom:mid",
0x0770:"top:topmost_contour_mid_point|bottom:mid",
0x0772:"top:topmost_contour_mid_point|bottom:mid",
0x0775:"top:topmost_contour_mid_point|bottom:bottommost_contours_mid_point",
0x0776:"top:topmost_contour_mid_point|bottom:bottommost_contours_mid_point",
0x0777:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x077C:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x077D:"top:topmost_contour_mid_point|bottom:mid",
0x077E:"top:topmost_contour_mid_point|bottom:mid",
0x077F:"top:topmost_contour_mid_point|bottom:mid",
0x08A0:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x08A1:"top:topmost_contour_mid_point(closer)|bottom:bottommost_contour_mid_point",
0x08A2:"top:topmost_contours_mid_point|bottom:bottommost_contour_mid_point",
0x08A3:"top:topmost_contours_mid_point|bottom:mid",
0x08A4:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x08A5:"top:topmost_contours_mid_point|bottom:bottommost_contour_mid_point",
0x08A6:"top:avarage_extrema|bottom:mid",
0x08A7:"top:topmost_contour_mid_point|bottom:avarage_extrema_center",
0x08A8:"top:topmost_contour_mid_point(closer)|bottom:bottommost_contours_mid_point",
0x08AF:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x08B0:"top:kaf|bottom:bottommost_contour_mid_point",
0x08B3:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x08B4:"top:kaf|bottom:bottommost_contour_mid_point"
}
non_Unicode_base_glyphs_dict_init ={
0x0620:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x063B:"top:topmost_contour_mid_point|bottom:mid",
0x063C:"top:kaf|bottom:bottommost_contour_mid_point",
0x063D:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contours_mid_point",
0x063E:"top:topmost_contours_mid_point|bottom:bottommost_contours_mid_point",
0x063F:"top:avarage_topmost_contour_mid_point|bottom:bottommost_contours_mid_point",
0x066F:"top:avarage_extrema|bottom:avarage_extrema",
0x067C:"top:topmost_contours_mid_point|bottom:avarage_bottommost_contour_mid_point",
0x067D:"top:topmost_contours_mid_point|bottom:mid",
0x0681:"top:topmost_contour_mid_point(closer)|bottom:mid",
0x0682:"top:topmost_contour_mid_point|bottom:mid",
0x0685:"top:topmost_contour_mid_point|bottom:mid",
0x069A:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x069B:"top:BIG_y_extrema|bottom:avarage_extrema",
0x069C:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x069D:"top:avarage_extrema|bottom:bottommost_contours_mid_point",
0x069E:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x06A0:"top:topmost_contour_mid_point|bottom:mid",
0x06A1:"top:avarage_extrema|bottom:mid",
0x06A2:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x06A3:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06A5:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x06AA:"top:kaf|bottom:mid",
0x06AB:"top:kaf|bottom:mid",
0x06AC:"top:topmost_contour_mid_point|bottom:mid",
0x06AE:"top:kaf|bottom:bottommost_contour_mid_point",
0x06B0:"top:kaf|bottom:mid",
0x06B2:"top:kaf|bottom:bottommost_contours_mid_point",
0x06B4:"top:topmost_contour_mid_point|bottom:mid",
0x06B5:"top:topmost_contour_mid_point|bottom:mid",
0x06B6:"top:topmost_contour_mid_point|bottom:mid",
0x06B7:"top:topmost_contour_mid_point|bottom:mid",
0x06B8:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x06B9:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06BC:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06BF:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06CE:"top:topmost_contour_mid_point|bottom:bottommost_contours_mid_point",
0x06FA:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06FB:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06FC:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x06FF:"top:topmost_contour_mid_point|bottom:avarage_extrema",
0x0750:"top:avarage_extrema|bottom:bottommost_contours_mid_point",
0x0751:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x0752:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x0753:"top:topmost_contours_mid_point|bottom:bottommost_contours_mid_point",
0x0754:"top:topmost_contour_mid_point|bottom:bottommost_contours_mid_point",
0x0755:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x0756:"top:topmost_contour_mid_point|bottom:mid",
0x0757:"top:topmost_contours_mid_point|bottom:mid",
0x0758:"top:avarage_extrema|bottom:bottommost_contours_mid_point",
0x075C:"top:topmost_contours_mid_point|bottom:mid",
0x075D:"top:topmost_contours_mid_point|bottom:mid",
0x075E:"top:topmost_contours_mid_point|bottom:mid",
0x075F:"top:topmost_contour_mid_point|bottom:mid",
0x0760:"top:avarage_extrema|bottom:bottommost_contours_mid_point",
0x0761:"top:avarage_extrema|bottom:bottommost_contours_mid_point",
0x0762:"top:avarage_topmost_contour_mid_point|bottom:mid",
0x0763:"top:topmost_contour_mid_point|bottom:mid",
0x0764:"top:kaf|bottom:bottommost_contours_mid_point",
0x0765:"top:topmost_contour_mid_point|bottom:avarage_extrema_center",
0x0766:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x0768:"top:topmost_contour_mid_point|bottom:mid",
0x0769:"top:topmost_contour_mid_point|bottom:mid",
0x076A:"top:avarage_extrema|bottom:mid",
0x076D:"top:topmost_contour_mid_point|bottom:mid",
0x076E:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x076F:"top:topmost_contour_mid_point|bottom:mid",
0x0770:"top:topmost_contour_mid_point|bottom:mid",
0x0772:"top:topmost_contour_mid_point|bottom:mid",
0x0775:"top:topmost_contour_mid_point|bottom:bottommost_contours_mid_point",
0x0776:"top:topmost_contour_mid_point|bottom:bottommost_contours_mid_point",
0x0777:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x077C:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x077D:"top:topmost_contour_mid_point|bottom:mid",
0x077E:"top:topmost_contour_mid_point|bottom:mid",
0x077F:"top:topmost_contour_mid_point|bottom:mid",
0x08A0:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x08A1:"top:topmost_contour_mid_point(closer)|bottom:bottommost_contour_mid_point",
0x08A2:"top:topmost_contours_mid_point|bottom:bottommost_contour_mid_point",
0x08A3:"top:topmost_contours_mid_point|bottom:mid",
0x08A4:"top:topmost_contour_mid_point|bottom:bottommost_contour_mid_point",
0x08A5:"top:topmost_contours_mid_point|bottom:bottommost_contour_mid_point",
0x08A6:"top:avarage_extrema|bottom:mid",
0x08A7:"top:topmost_contour_mid_point|bottom:avarage_extrema_center",
0x08A8:"top:topmost_contour_mid_point(closer)|bottom:bottommost_contours_mid_point",
0x08AF:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x08B0:"top:kaf|bottom:bottommost_contour_mid_point",
0x08B3:"top:avarage_extrema|bottom:bottommost_contour_mid_point",
0x08B4:"top:kaf|bottom:bottommost_contour_mid_point"
}
non_Unicode_base_glyphs_dict ={}
ligature_glyphs_dict = {
0xFEF5:"top#0:extrema|top#1:topmost_contour_mid_point|bottom#0:extrema|bottom#1:extrema",             #ﻵ
0xFEF6:"top#0:extrema|top#1:topmost_contour_mid_point|bottom#0:extrema|bottom#1:extrema",             #ﻶ
0xFEF7:"top#0:extrema|top#1:topmost_contour_mid_point(closer)|bottom#0:extrema|bottom#1:extrema",     #ﻷ
0xFEF8:"top#0:extrema|top#1:topmost_contour_mid_point(closer)|bottom#0:extrema|bottom#1:extrema",     #ﻸ
0xFEF9:"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:bottommost_contour_mid_point(closer)",  #ﻹ
0xFEFA:"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:bottommost_contour_mid_point(closer)",  #ﻺ
0xFEFB:"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",                               #ﻻ
0xFEFC:"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",                               #ﻼ
}
unprocessed_non_Unicode_ligature_glyphs_dict ={
(0x06B5,'init',0xFE8E,'same'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0x06B5,'medi',0xFE8E,'same'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0x06B6,'init',0xFE8E,'same'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0x06B6,'medi',0xFE8E,'same'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0x06B7,'init',0xFE8E,'same'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0x06B7,'medi',0xFE8E,'same'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0x06B8,'init',0xFE8E,'same'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0x06B8,'medi',0xFE8E,'same'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0x076A,'init',0xFE8E,'same'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0x076A,'medi',0xFE8E,'same'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0x08A6,'init',0xFE8E,'same'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0x08A6,'medi',0xFE8E,'same'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0xFEDF,'same',0x0672,'fina'):"top#0:extrema|top#1:topmost_contour_mid_point(closer)|bottom#0:extrema|bottom#1:extrema",
(0xFEDF,'same',0x0673,'fina'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0xFEDF,'same',0x0675,'fina'):"top#0:topmost_contour_mid_point(closer)|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0xFEDF,'same',0x0773,'fina'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0xFEDF,'same',0x0774,'fina'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0xFEDF,'same',0xFB51,'same'):"top#0:extrema|top#1:topmost_contour_mid_point|bottom#0:extrema|bottom#1:extrema",
(0xFEE0,'same',0x0672,'fina'):"top#0:extrema|top#1:topmost_contour_mid_point(closer)|bottom#0:extrema|bottom#1:extrema",
(0xFEE0,'same',0x0673,'fina'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0xFEE0,'same',0x0675,'fina'):"top#0:topmost_contour_mid_point(closer)|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0xFEE0,'same',0x0773,'fina'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0xFEE0,'same',0x0774,'fina'):"top#0:extrema|top#1:extrema|bottom#0:extrema|bottom#1:extrema",
(0xFEE0,'same',0xFB51,'same'):"top#0:extrema|top#1:topmost_contour_mid_point|bottom#0:extrema|bottom#1:extrema"
}
processed_non_Unicode_ligature_glyphs_dict ={}
unicode_and_form_to_non_Unicode_glyphname_dict = {}

'''
def glyph_bbox_bottom_mid_first_inShape_point(this_glyph):
    if str(this_glyph).isnumeric():
        glyph = font[ff.nameFromUnicode(this_glyph)]
    else:
        glyph = font[this_glyph]
    glyph.preserveLayerAsUndo()
    for ref in glyph.references:
        glyph.unlinkRef()
    glyph_bbox = glyph.boundingBox()
    glyph_bbox_bottom_mid_point = ((glyph_bbox[2]+glyph_bbox[0])/2,glyph_bbox[1]) #((x_max+x_min)/2,y_min)
    glyph_bbox_height = glyph_bbox[3]-glyph_bbox[1] #y-max - y_min
    font.layers.add('temp_layer',False)
    glyph.setLayer(glyph.layers['Fore'], 'temp_layer')
    full_on_curve_points_list_before = []
    for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
        points = list(contour)
        on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
        for i in range(len(on_curve_points_list)):
            full_on_curve_points_list_before.append(on_curve_points_list[i])
    for step in range(int(round(glyph_bbox_height))):
        full_on_curve_points_list_after = []
        point = tuple(map(sum, zip(glyph_bbox_bottom_mid_point, (0,step)))) 
        print(point)
        pen = glyph.glyphPen()
        pen.moveTo(point)
        pen.lineTo((glyph_bbox_bottom_mid_point[0]-10, glyph_bbox_bottom_mid_point[1]-10))
        pen.lineTo((glyph_bbox_bottom_mid_point[0]+10, glyph_bbox_bottom_mid_point[1]-10))
        pen.lineTo(point)
        pen.closePath()
        glyph.setLayer(glyph.layers['temp_layer'] + glyph.layers['Fore'], 'Fore')
        glyph.removeOverlap()
        glyph.setLayer(glyph.layers['Fore'], 'Back')
        for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
            points = list(contour)
            on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
            for i in range(len(on_curve_points_list)):
                full_on_curve_points_list_after.append(on_curve_points_list[i])
        glyph.setLayer(glyph.layers['temp_layer'], 'Fore')
        if ((len(full_on_curve_points_list_after)-len(full_on_curve_points_list_before)-3)/4)%2:
            for layer in font.layers:
                if layer == 'temp_layer':
                    del font.layers[layer]
            #glyph.doUndoLayer()
            return point[1]
    for layer in font.layers:
        if layer == 'temp_layer':
            del font.layers[layer]
    #glyph.doUndoLayer()
    return glyph_bbox[3]
'''
def y_extrema_ignore_side(this_glyph,ignore_side,extrema_vert_side):
    if str(this_glyph).isnumeric():
        glyph = font[ff.nameFromUnicode(this_glyph)]
    else:
        glyph = font[this_glyph]
    glyph.preserveLayerAsUndo()
    for ref in glyph.references:
        glyph.unlinkRef()
    glyph.addExtrema('all')
    glyph.removeOverlap()
    glyph.simplify()
    full_on_curve_points_list = []
    for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
        points = list(contour)
        on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
        for i in range(len(on_curve_points_list)):
            full_on_curve_points_list.append(on_curve_points_list[i])
    #ignore_left:
    if ignore_side == 'ignore_left':
        if extrema_vert_side == 'y_max':
            full_on_curve_points_list_ignore_left_max = [i for i in full_on_curve_points_list if i[0]>=(avarage_y_max_extrema[0] + ignore_left_shift)]
            y_max_extrema = max(full_on_curve_points_list_ignore_left_max, key=lambda x:x[1])
            for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
                points = list(contour)
                on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
            x_avarage_list_in_y_max_ignore_left = []
            for point in full_on_curve_points_list_ignore_left_max:
                if point[1] >= y_max_extrema[1] - y_extrema_avarge_tolerance:
                    x_avarage_list_in_y_max_ignore_left.append(point)
            avarage_y_max_extrema_ignore_left = (sum(i[0] for i in x_avarage_list_in_y_max_ignore_left)/len(x_avarage_list_in_y_max_ignore_left),y_max_extrema[1])
            glyph.doUndoLayer()
            return avarage_y_max_extrema_ignore_left
        elif extrema_vert_side == 'y_min':
            full_on_curve_points_list_ignore_left_min = [i for i in full_on_curve_points_list if i[0]>=(avarage_y_min_extrema[0] + ignore_left_shift)]
            y_min_extrema = min(full_on_curve_points_list_ignore_left_min, key=lambda x:x[1])
            for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
                points = list(contour)
                on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
            x_avarage_list_in_y_min_ignore_left = []
            for point in full_on_curve_points_list_ignore_left_min:
                if point[1] < y_min_extrema[1] + y_extrema_avarge_tolerance:
                    x_avarage_list_in_y_min_ignore_left.append(point)
            avarage_y_min_extrema_ignore_left = (sum(i[0] for i in x_avarage_list_in_y_min_ignore_left)/len(x_avarage_list_in_y_min_ignore_left),y_min_extrema[1])
            glyph.doUndoLayer()
            return avarage_y_min_extrema_ignore_left
    #ignore_left_center:
    if ignore_side == 'ignore_left_center':
        if extrema_vert_side == 'y_max':
            point_to_remove = []
            full_on_curve_points_list_ignore_left_max = [i for i in full_on_curve_points_list if i[0]>=(avarage_y_max_extrema[0] + ignore_left_shift)]
            ignore_connection_circle_raduce = ignore_connection_circle_raduce_factor*2*strok_mid()
            for point in full_on_curve_points_list_ignore_left_max:
                if (point[0]**2 + point[1]**2)**0.5 <= ignore_connection_circle_raduce or (((point[0] - glyph.boundingBox()[2])**2 + point[1]**2)**0.5 <= ignore_connection_circle_raduce):
                    point_to_remove.append(point)
            full_on_curve_points_list_ignore_left_center_max = [x for x in full_on_curve_points_list_ignore_left_max if x not in point_to_remove]
            y_max_extrema = max(full_on_curve_points_list_ignore_left_center_max, key=lambda x:x[1])
            for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
                points = list(contour)
                on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
            x_avarage_list_in_y_max_ignore_left = []
            for point in full_on_curve_points_list_ignore_left_center_max:
                if point[1] >= y_max_extrema[1] - y_extrema_avarge_tolerance:
                    x_avarage_list_in_y_max_ignore_left.append(point)
            avarage_y_max_extrema_ignore_left = (sum(i[0] for i in x_avarage_list_in_y_max_ignore_left)/len(x_avarage_list_in_y_max_ignore_left),y_max_extrema[1])
            glyph.doUndoLayer()
            return avarage_y_max_extrema_ignore_left
        elif extrema_vert_side == 'y_min':
            point_to_remove = []
            full_on_curve_points_list_ignore_left_min = [i for i in full_on_curve_points_list if i[0]>=(avarage_y_min_extrema[0] + ignore_left_shift)]
            ignore_connection_circle_raduce = ignore_connection_circle_raduce_factor*2*strok_mid()
            for point in full_on_curve_points_list_ignore_left_min:
                if (point[0]**2 + point[1]**2)**0.5 <= ignore_connection_circle_raduce or (((point[0] - glyph.boundingBox()[2])**2 + point[1]**2)**0.5 <= ignore_connection_circle_raduce):
                    point_to_remove.append(point)
            full_on_curve_points_list_ignore_left_center_min = [x for x in full_on_curve_points_list_ignore_left_min if x not in point_to_remove]
            y_min_extrema = min(full_on_curve_points_list_ignore_left_center_min, key=lambda x:x[1])
            for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
                points = list(contour)
                on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
            x_avarage_list_in_y_min_ignore_left = []
            for point in full_on_curve_points_list_ignore_left_center_min:
                if point[1] < y_min_extrema[1] + y_extrema_avarge_tolerance:
                    x_avarage_list_in_y_min_ignore_left.append(point)
            avarage_y_min_extrema_ignore_left = (sum(i[0] for i in x_avarage_list_in_y_min_ignore_left)/len(x_avarage_list_in_y_min_ignore_left),y_min_extrema[1])
            glyph.doUndoLayer()
            return avarage_y_min_extrema_ignore_left
    #ignore_right:
    if ignore_side == 'ignore_right':
        if extrema_vert_side == 'y_max':
            full_on_curve_points_list_ignore_right_max = [i for i in full_on_curve_points_list if i[0]<=(avarage_y_max_extrema[0] - ignore_right_shift)]
            y_max_extrema = max(full_on_curve_points_list_ignore_right, key=lambda x:x[1])
            print(full_on_curve_points_list_ignore_right_max)
            for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
                points = list(contour)
                on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
            x_avarage_list_in_y_max_ignore_right = []
            for point in full_on_curve_points_list_ignore_right_max:
                if point[1] >= y_max_extrema[1] - y_extrema_avarge_tolerance:
                    x_avarage_list_in_y_max_ignore_right.append(point)
            avarage_y_max_extrema_ignore_right = (sum(i[0] for i in x_avarage_list_in_y_max_ignore_right)/len(x_avarage_list_in_y_max_ignore_right),y_max_extrema[1])
            glyph.doUndoLayer()
            return avarage_y_max_extrema_ignore_right
        elif extrema_vert_side == 'y_min':
            full_on_curve_points_list_ignore_right_min = [i for i in full_on_curve_points_list if i[0]<=(avarage_y_min_extrema[0] - ignore_right_shift)]
            y_min_extrema = min(full_on_curve_points_list_ignore_right_min, key=lambda x:x[1])
            for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
                points = list(contour)
                on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
            x_avarage_list_in_y_min_ignore_right = []
            for point in full_on_curve_points_list_ignore_right_min:
                if point[1] < y_min_extrema[1] + y_extrema_avarge_tolerance:
                    x_avarage_list_in_y_min_ignore_right.append(point)
            avarage_y_min_extrema_ignore_right = (sum(i[0] for i in x_avarage_list_in_y_min_ignore_right)/len(x_avarage_list_in_y_min_ignore_right),y_min_extrema[1])
            glyph.doUndoLayer()
            return avarage_y_min_extrema_ignore_right

def vertical_avarage_side_most(this_glyph,side):
    if str(this_glyph).isnumeric():
        glyph = font[ff.nameFromUnicode(this_glyph)]
    else:
        glyph = font[this_glyph]
    max_y_point = []
    min_y_point = []
    list_of_avarage_y = []
    list_of_x_max = []
    list_of_x_min = []
    glyph.preserveLayerAsUndo()
    for ref in glyph.references:
        glyph.unlinkRef()
    glyph.addExtrema('all')
    glyph.removeOverlap()
    glyph.simplify()
    for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
        points = list(contour)
        on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
        avarage_y = sum(n for _, n in on_curve_points_list)/len(on_curve_points_list)
        max_y_point.append(max(on_curve_points_list, key=lambda x:x[1])[1])
        min_y_point.append(min(on_curve_points_list, key=lambda x:x[1])[1])
        list_of_avarage_y.append(avarage_y)
        list_of_x_max.append(max(on_curve_points_list)[0])
        list_of_x_min.append(min(on_curve_points_list)[0])
    if side == 'up':
        index = list_of_avarage_y.index(max(list_of_avarage_y))
        glyph.doUndoLayer()
        return ((list_of_x_max[index]+list_of_x_min[index])/2,max_y_point[index])
    if side == 'down':
        index = list_of_avarage_y.index(min(list_of_avarage_y))
        glyph.doUndoLayer()
        return ((list_of_x_max[index]+list_of_x_min[index])/2,min_y_point[index])

def y_max_ignore_top_extrema(this_glyph):
    if str(this_glyph).isnumeric():
        glyph = font[ff.nameFromUnicode(this_glyph)]
    else:
        glyph = font[this_glyph]
    full_on_curve_points_list = []
    list_of_y_max_extrema_points_ignore_top_extrema = []
    glyph.preserveLayerAsUndo()
    for ref in glyph.references:
        glyph.unlinkRef()
    glyph.addExtrema("all")
    glyph.removeOverlap()
    for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
        points = list(contour)
        on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
        for i in range(len(on_curve_points_list)):
            full_on_curve_points_list.append(on_curve_points_list[i])
    on_curve_points_list_ignore_top_extrema = [i for i in full_on_curve_points_list if i[1] <= glyph.boundingBox()[3]*(1-ignore_top_extrema_ratio)]
    y_max_ignore_top_extrema = list(max(on_curve_points_list_ignore_top_extrema, key=lambda x:x[1]))
    x_avarage_list = []
    for point in full_on_curve_points_list:
        if point[1] >= y_max_ignore_top_extrema[1]*(1-ignore_top_extrema_ratio) and point[1] <= y_max_ignore_top_extrema[1]:
            x_avarage_list.append(point[0])
    x_avarage_list = list(dict.fromkeys(x_avarage_list)) #remove duplicates
    y_max_ignore_top_extrema[0] = round(sum(x_avarage_list)/len(x_avarage_list))
    glyph.doUndoLayer()
    return y_max_ignore_top_extrema

def y_max_extrema_liga(lig_type,part,single_or_avarage):
    if lig_type == 'double':
        x_avarage_list = []
        divide_line = glyph.width*double_ligature_divide_ratio
        first_part_on_curve_points_list = [i for i in full_on_curve_points_list if i[0] >= divide_line]
        secound_part_on_curve_points_list = [i for i in full_on_curve_points_list if i[0] <= divide_line]
        if part == 'first_part':
            y_max_extrema_liga = max(first_part_on_curve_points_list, key=lambda x:x[1])
            if single_or_avarage == 'single':
                return y_max_extrema_liga
            for point in first_part_on_curve_points_list:
                if point[1] >= y_max_extrema_liga[1] - y_extrema_avarge_tolerance:
                    x_avarage_list.append(point[0])
            x_avarage_list = list(dict.fromkeys(x_avarage_list)) #remove duplicates
            avarage_y_max_extrema_liga = (round(sum(x_avarage_list)/len(x_avarage_list)),y_max_extrema_liga[1])
            if single_or_avarage == 'avarage':
                return avarage_y_max_extrema_liga
        if part == 'secound_part':
            y_max_extrema_liga = max(secound_part_on_curve_points_list, key=lambda x:x[1])
            if single_or_avarage == 'single':
                return y_max_extrema_liga
            for point in secound_part_on_curve_points_list:
                if point[1] >= y_max_extrema_liga[1] - y_extrema_avarge_tolerance:
                    x_avarage_list.append(point[0])
            x_avarage_list = list(dict.fromkeys(x_avarage_list)) #remove duplicates
            avarage_y_max_extrema_liga = (round(sum(x_avarage_list)/len(x_avarage_list)),y_max_extrema_liga[1])
            if single_or_avarage == 'avarage':
                return avarage_y_max_extrema_liga
def y_min_extrema_liga(lig_type,part,this_glyph):
    if lig_type == 'double':
        x_avarage_list = []
        divide_line = glyph.width*double_ligature_divide_ratio
        first_part_on_curve_points_list = [i for i in full_on_curve_points_list if i[0] >= divide_line]
        secound_part_on_curve_points_list = [i for i in full_on_curve_points_list if i[0] <= divide_line]
        if part == 'first_part':
            y_min_extrema_liga = min(first_part_on_curve_points_list, key=lambda x:x[1])
            if single_or_avarage == 'single':
                return y_min_extrema_liga
            for point in first_part_on_curve_points_list:
                if point[1] >= y_min_extrema_liga[1] - y_extrema_avarge_tolerance:
                    x_avarage_list.append(point[0])
            x_avarage_list = list(dict.fromkeys(x_avarage_list)) #remove duplicates
            avarage_y_min_extrema_liga = (round(sum(x_avarage_list)/len(x_avarage_list)),y_min_extrema_liga[1])
            if single_or_avarage == 'avarage':
                return avarage_y_min_extrema_liga
        if part == 'secound_part':
            y_min_extrema_liga = min(secound_part_on_curve_points_list, key=lambda x:x[1])
            if single_or_avarage == 'single':
                return y_min_extrema_liga
            for point in secound_part_on_curve_points_list:
                if point[1] >= y_min_extrema_liga[1] - y_extrema_avarge_tolerance:
                    x_avarage_list.append(point[0])
            x_avarage_list = list(dict.fromkeys(x_avarage_list)) #remove duplicates
            avarage_y_min_extrema_liga = (round(sum(x_avarage_list)/len(x_avarage_list)),y_min_extrema_liga[1])
            if single_or_avarage == 'avarage':
                return avarage_y_min_extrema_liga

def avarage_y_min_extrema_center(this_glyph):
    ignore_connection_circle_raduce = ignore_connection_circle_raduce_factor*2*strok_mid()
    x_avarage_list_in_y_min_center = []
    full_on_curve_points_list_center = []
    point_to_remove = []
    if str(this_glyph).isnumeric():
        glyph = font[ff.nameFromUnicode(this_glyph)]
    else:
        glyph = font[this_glyph]
    glyph.preserveLayerAsUndo()
    for ref in glyph.references:
        glyph.unlinkRef()
    glyph.addExtrema('all')
    glyph.removeOverlap()
    glyph.simplify()
    for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
        points = list(contour)
        on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
        #remove near connection points:
        for point in on_curve_points_list:
            if (point[0]**2 + point[1]**2)**0.5 <= ignore_connection_circle_raduce or (((point[0] - glyph.boundingBox()[2])**2 + point[1]**2)**0.5 <= ignore_connection_circle_raduce):
                point_to_remove.append(point)
        on_curve_points_list_center = [x for x in on_curve_points_list if x not in point_to_remove]
        for i in range(len(on_curve_points_list_center)):
            full_on_curve_points_list_center.append(on_curve_points_list_center[i])
    for point in full_on_curve_points_list_center:
        if point[1] < y_min_extrema[1] + y_extrema_avarge_tolerance:
            x_avarage_list_in_y_min_center.append(point)
    x_avarage_list_in_y_min_center = list(dict.fromkeys(x_avarage_list_in_y_min_center)) #remove duplicates
    avarage_y_min_extrema_center = (sum(i[0] for i in x_avarage_list_in_y_min_center)/len(x_avarage_list_in_y_min_center),sum(i[1] for i in x_avarage_list_in_y_min_center)/len(x_avarage_list_in_y_min_center))
    glyph.doUndoLayer()
    return avarage_y_min_extrema_center
    
def sidemost_contour_mid_point(this_glyph,y_on_curve_extermum):
    if str(this_glyph).isnumeric():
        glyph = font[ff.nameFromUnicode(this_glyph)]
    else:
        glyph = font[this_glyph]
    glyph.preserveLayerAsUndo()
    for ref in glyph.references:
        glyph.unlinkRef()
    glyph.addExtrema('all')
    glyph.removeOverlap()
    glyph.simplify()
    for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
        points = list(contour)
        on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
        if y_on_curve_extermum in on_curve_points_list:
            x_min_point = min(on_curve_points_list)[0]
            x_max_point = max(on_curve_points_list)[0]
    glyph.doUndoLayer()
    return ((x_max_point+x_min_point)/2)
    
def sidemost_contour_mid_point_liga(lig_type,part,this_glyph,side):
    if str(this_glyph).isnumeric():
        glyph = font[ff.nameFromUnicode(this_glyph)]
    else:
        glyph = font[this_glyph]
    if lig_type == 'double':
        glyph.preserveLayerAsUndo()
        for ref in glyph.references:
            glyph.unlinkRef()
        glyph.addExtrema('all')
        glyph.removeOverlap()
        glyph.simplify()
        divide_line = glyph.width*double_ligature_divide_ratio
        full_on_curve_points_list = []
        for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
            points = list(contour)
            on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
            for i in range(len(on_curve_points_list)):
                full_on_curve_points_list.append(on_curve_points_list[i])
        first_part_on_curve_points_list = [i for i in full_on_curve_points_list if i[0] >= divide_line]
        secound_part_on_curve_points_list = [i for i in full_on_curve_points_list if i[0] <= divide_line]
        for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
            points = list(contour)
            on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
            if part == 'first_part':
                if side == 'up':
                    for i in range(len(on_curve_points_list)):
                        if on_curve_points_list[i] == max(first_part_on_curve_points_list, key=lambda x:x[1]):
                            x_min_point = min(on_curve_points_list)[0]
                            x_max_point = max(on_curve_points_list)[0]
                            y_max_point = max(on_curve_points_list, key=lambda x:x[1])[1]
                            glyph.doUndoLayer()
                            return ((x_max_point+x_min_point)/2,y_max_point)
                elif side == 'down':
                    for i in range(len(on_curve_points_list)):
                        if on_curve_points_list[i] == min(first_part_on_curve_points_list, key=lambda x:x[1]):
                            x_min_point = min(on_curve_points_list)[0]
                            x_max_point = max(on_curve_points_list)[0]
                            y_min_point = min(on_curve_points_list, key=lambda x:x[1])[1]
                            glyph.doUndoLayer()
                            return ((x_max_point+x_min_point)/2,y_min_point)
            if part == 'secound_part':
                if side == 'up':
                    for i in range(len(on_curve_points_list)):
                        if on_curve_points_list[i] == max(secound_part_on_curve_points_list, key=lambda x:x[1]):
                            x_min_point = min(on_curve_points_list)[0]
                            x_max_point = max(on_curve_points_list)[0]
                            y_max_point = max(on_curve_points_list, key=lambda x:x[1])[1]
                            glyph.doUndoLayer()
                            return ((x_max_point+x_min_point)/2,y_max_point)
                elif side == 'down':
                    for i in range(len(on_curve_points_list)):
                        if on_curve_points_list[i] == min(secound_part_on_curve_points_list, key=lambda x:x[1]):
                            x_min_point = min(on_curve_points_list)[0]
                            x_max_point = max(on_curve_points_list)[0]
                            y_min_point = min(on_curve_points_list, key=lambda x:x[1])[1]
                            glyph.doUndoLayer()
                            return ((x_max_point+x_min_point)/2,y_min_point)

def kaf_top_anchor_find(this_glyph):
    if str(this_glyph).isnumeric():
        glyph = font[ff.nameFromUnicode(this_glyph)]
        glyph_bbox = font[ff.nameFromUnicode(this_glyph)].boundingBox()
    else:
        glyph = font[this_glyph]
        glyph_bbox = font[this_glyph].boundingBox()
    glyph.preserveLayerAsUndo()
    list_of_y_max_extrema_points = []
    for ref in glyph.references:
        glyph.unlinkRef()
    glyph.addExtrema('all')
    glyph.removeOverlap()
    glyph.simplify()
    for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
        points = list(contour)
        on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
        max_extrema_point_in_y = max(on_curve_points_list, key=lambda x:x[1])
        list_of_y_max_extrema_points.append(max_extrema_point_in_y)
    y_max_extrema = max(list_of_y_max_extrema_points, key=lambda x:x[1])
    for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
        points = list(contour)
        on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
        max_extrema_point_in_y = max(on_curve_points_list, key=lambda x:x[1])
        if y_max_extrema in on_curve_points_list:
            y_max_index = list(x for x, y in enumerate(on_curve_points_list) if y[1] == max_extrema_point_in_y[1])[0]
            if contour.isClockwise():
                for i in range(len(on_curve_points_list)):
                    kaf_slope = (on_curve_points_list[y_max_index][1]-on_curve_points_list[y_max_index-1][1])/(on_curve_points_list[y_max_index][0]-on_curve_points_list[y_max_index-1][0])
                    seg_slope = (on_curve_points_list[y_max_index-i][1]-on_curve_points_list[y_max_index-1-i][1])/(on_curve_points_list[y_max_index-i][0]-on_curve_points_list[y_max_index-1-i][0])
                    if abs(seg_slope - kaf_slope) >= kaf_slop_tolerance :
                        kaf_break_point = on_curve_points_list[y_max_index-i]
                        break
            else:
                for i in range(len(on_curve_points_list)):
                    kaf_slope = (on_curve_points_list[y_max_index][1]-on_curve_points_list[y_max_index-1][1])/(on_curve_points_list[y_max_index][0]-on_curve_points_list[y_max_index-1][0])
                    seg_slope = (on_curve_points_list[y_max_index+i][1]-on_curve_points_list[y_max_index-1+i][1])/(on_curve_points_list[y_max_index+i][0]-on_curve_points_list[y_max_index-1+i][0])
                    if abs(seg_slope-kaf_slope) >= kaf_slop_tolerance :
                        kaf_break_point = on_curve_points_list[y_max_index+i]
                        break
    glyph.doUndoLayer()
    return ((y_max_extrema[0]+kaf_break_point[0])/2,(y_max_extrema[1]+kaf_break_point[1])/2)

def name_from_unicode_and_form(form,this_glyph):
    if form == 'same':
        return ff.nameFromUnicode(this_glyph)
    else:
        return unicode_and_form_to_non_Unicode_glyphname_dict[(form,this_glyph)]
        
def strok_mid():
    if font[ff.nameFromUnicode(0x0640)]:
        tatweel = font[ff.nameFromUnicode(0x0640)]
        tatweel_height = tatweel.boundingBox()[3]-tatweel.boundingBox()[1]
        return tatweel_height/2
    else:
        return 0

def BIG_y_extrema(left_limit,right_limit):
    list_of_points_above_BIG_y_extrema = []
    for point in full_on_curve_points_list:
        if y_max_extrema[1] >= 0:
            if point[1] >= y_max_extrema[1]*normalized_BIG_y_extrema_avarge_tolerance_ratio:
                if point[0] <= right_limit and point[0] >= left_limit:
                    list_of_points_above_BIG_y_extrema.append(point)
    return ((min(list_of_points_above_BIG_y_extrema)[0]+max(list_of_points_above_BIG_y_extrema)[0])/2,sum(point[1] for point in list_of_points_above_BIG_y_extrema)/len(list_of_points_above_BIG_y_extrema))

print('---------------------------------------------------------------------')
print('----------------------╭───────────────────────╮----------------------')
print('----------------------│  AutoMark-v0.1(beta3) │----------------------')
print('----------------------│   a fontamin product  │----------------------')
print('----------------------│      License: MIT     │----------------------')
print('----------------------╰───────────────────────╯----------------------')
print('---------------------------------------------------------------------')
print('Optional Parameters:')
print('--normalized_mark_to_mark_gap',args.normalized_mark_to_mark_gap,'(default = 0.04)')
print('--normalized_mark_to_base_gap',args.normalized_mark_to_base_gap,'(default = 0.12)')
print('--normalized_depth_in_extrema',args.normalized_depth_in_extrema,'(default = 0.08)')
print('--normalized_ignore_left_shift',args.normalized_ignore_left_shift,'(default = 0.05)')
print('--normalized_ignore_right_shift',args.normalized_ignore_right_shift,'(default = 0.05)')
print('--kaf_slop_tolerance',kaf_slop_tolerance,'(default = 0.2)')
print('--double_ligature_divide_ratio',double_ligature_divide_ratio,'(default = 0.5)')
print('--normalized_y_extrema_avarge_tolerance_ratio',normalized_y_extrema_avarge_tolerance_ratio,'(default = 0.01)')
print('--normalized_BIG_y_extrema_avarge_tolerance_ratio',normalized_BIG_y_extrema_avarge_tolerance_ratio,'(default = 0.5)')
print('---------------------------------------------------------------------')

if __name__ == '__main__':
    if os.path.split(args.input_file)[0]:
        os.chdir(os.path.split(args.input_file)[0])
    for file in os.listdir(): 
        if file == os.path.split(args.input_file)[1]:
            font = ff.open(file)
            font.encoding = "UnicodeFull"
            for lookup_name in font.gsub_lookups:
                if font.getLookupInfo(lookup_name)[0]=='gsub_ligature' and font.getLookupInfo(lookup_name)[2][0][0]=='ccmp':
                    print('Adding mark ligatures...')
                    ccmp_subtabs = font.getLookupSubtables(lookup_name)
                    for glyph in font.glyphs():
                        if font[glyph.glyphname].getPosSub(ccmp_subtabs[0]):
                            first_sub = font[glyph.glyphname].getPosSub(ccmp_subtabs[0])[0][2]
                            secound_sub = font[glyph.glyphname].getPosSub(ccmp_subtabs[0])[0][3]
                            if ff.unicodeFromName(first_sub) or ff.unicodeFromName(first_sub) in top_mark_glyphs:
                                top_ligature_mark_glyphs.append(glyph.glyphname)
                            if ff.unicodeFromName(first_sub) and ff.unicodeFromName(first_sub) in bottom_mark_glyphs:
                                bottom_ligature_mark_glyphs.append(glyph.glyphname)
            for lookup_name in font.gsub_lookups:
                try:
                    if font.getLookupInfo(lookup_name)[0]=='gsub_single' and font.getLookupInfo(lookup_name)[2][0][0]=='fina':
                        fina_subtabs = font.getLookupSubtables(lookup_name)
                        for glyph in font.glyphs():
                            if font[glyph.glyphname].getPosSub(fina_subtabs[0]):
                                secound_sub = font[glyph.glyphname].getPosSub(fina_subtabs[0])[0][2]
                                if ff.unicodeFromName(secound_sub) == -1:
                                    for codepoint in non_Unicode_base_glyphs_dict_fina.keys():
                                        if codepoint == ff.unicodeFromName(glyph.glyphname):
                                            non_Unicode_base_glyphs_dict[secound_sub] = non_Unicode_base_glyphs_dict_fina[codepoint]
                                            unicode_and_form_to_non_Unicode_glyphname_dict[tuple(('fina',glyph.unicode))] = secound_sub
                except IndexError:
                    pass
            for lookup_name in font.gsub_lookups:
                try:
                    if font.getLookupInfo(lookup_name)[0]=='gsub_single' and font.getLookupInfo(lookup_name)[2][0][0]=='medi':
                        medi_subtabs = font.getLookupSubtables(lookup_name)
                        for glyph in font.glyphs():
                            if font[glyph.glyphname].getPosSub(medi_subtabs[0]):
                                secound_sub = font[glyph.glyphname].getPosSub(medi_subtabs[0])[0][2]
                                if ff.unicodeFromName(secound_sub) == -1:
                                    for codepoint in non_Unicode_base_glyphs_dict_medi.keys():
                                        if codepoint == ff.unicodeFromName(glyph.glyphname):
                                            non_Unicode_base_glyphs_dict[secound_sub] = non_Unicode_base_glyphs_dict_medi[codepoint]
                                            unicode_and_form_to_non_Unicode_glyphname_dict[tuple(('medi',glyph.unicode))] = secound_sub
                except IndexError:
                    pass
            for lookup_name in font.gsub_lookups:
                try:
                    if font.getLookupInfo(lookup_name)[0]=='gsub_single' and font.getLookupInfo(lookup_name)[2][0][0]=='init':
                        init_subtabs = font.getLookupSubtables(lookup_name)
                        for glyph in font.glyphs():
                            if font[glyph.glyphname].getPosSub(init_subtabs[0]):
                                secound_sub = font[glyph.glyphname].getPosSub(init_subtabs[0])[0][2]
                                if ff.unicodeFromName(secound_sub) == -1:
                                    for codepoint in non_Unicode_base_glyphs_dict_init.keys():
                                        if codepoint == ff.unicodeFromName(glyph.glyphname):
                                            non_Unicode_base_glyphs_dict[secound_sub] = non_Unicode_base_glyphs_dict_init[codepoint]
                                            unicode_and_form_to_non_Unicode_glyphname_dict[tuple(('init',glyph.unicode))] = secound_sub
                except IndexError:
                    pass
            ##creating processed non-Unicode ligature dict:
            for lookup_name in font.gsub_lookups:
                if font.getLookupInfo(lookup_name)[0]=='gsub_ligature' and font.getLookupInfo(lookup_name)[2][0][0] in ['liga','rlig']:
                    liga_subtabs = font.getLookupSubtables(lookup_name)
                    for glyph in font.glyphs():
                        if font[glyph.glyphname].getPosSub(liga_subtabs[0]):
                            secound_subs = [font[glyph.glyphname].getPosSub(liga_subtabs[0])[0][2],font[glyph.glyphname].getPosSub(liga_subtabs[0])[0][3]]
                            if ff.unicodeFromName(glyph.glyphname) == -1:
                                for item in unprocessed_non_Unicode_ligature_glyphs_dict.items():
                                    if name_from_unicode_and_form(item[0][1],item[0][0])==secound_subs[0] and name_from_unicode_and_form(item[0][3],item[0][2])==secound_subs[1]:
                                        processed_non_Unicode_ligature_glyphs_dict[glyph.glyphname] = unprocessed_non_Unicode_ligature_glyphs_dict[item[0]]
    
            # mkmk:
            print('Adding mkmk feature...')
            font.addLookup("top_mkmk", "gpos_mark2mark", 'right_to_left', (("mkmk",(("DFLT",("dflt")),("arab",("dflt")),("latn",("dflt")),)),))
            font.addLookupSubtable("top_mkmk", "top_mkmk-subtable")
            font.addAnchorClass("top_mkmk-subtable", "top_mark")
            font.addLookup("bottom_mkmk", "gpos_mark2mark", 'right_to_left', (("mkmk",(("DFLT",("dflt")),("arab",("dflt")),("latn",("dflt")),)),))
            font.addLookupSubtable("bottom_mkmk", "bottom_mkmk-subtable")
            font.addAnchorClass("bottom_mkmk-subtable", "bottom_mark")
            # mark_to_base:
            print('Adding mark feature(mark to base)...')
            font.addLookup("top_mark", "gpos_mark2base", 'right_to_left', (("mark",(("DFLT",("dflt")),("arab",("dflt")),("latn",("dflt")),)),))
            font.addLookupSubtable("top_mark", "top_mark-subtable")
            font.addAnchorClass("top_mark-subtable", "top")
            font.addLookup("bottom_mark", "gpos_mark2base", 'right_to_left', (("mark",(("DFLT",("dflt")),("arab",("dflt")),("latn",("dflt")),)),))
            font.addLookupSubtable("bottom_mark", "bottom_mark-subtable")
            font.addAnchorClass("bottom_mark-subtable", "bottom")
            # mark_to_ligature:
            print('Adding mark feature(mark to ligature)...')
            font.addLookup("top_mark_lig", "gpos_mark2ligature", 'right_to_left', (("mark",(("DFLT",("dflt")),("arab",("dflt")),("latn",("dflt")),)),))
            font.addLookupSubtable("top_mark_lig", "top_mark_lig-subtable")
            font.addAnchorClass("top_mark_lig-subtable", "top_lig")
            font.addLookup("bottom_mark_lig", "gpos_mark2ligature", 'right_to_left', (("mark",(("DFLT",("dflt")),("arab",("dflt")),("latn",("dflt")),)),))
            font.addLookupSubtable("bottom_mark_lig", "bottom_mark_lig-subtable")
            font.addAnchorClass("bottom_mark_lig-subtable", "bottom_lig")
            y_extrema_avarge_tolerance = round(normalized_y_extrema_avarge_tolerance_ratio * font.em)
            mark_to_mark_gap = normalized_mark_to_mark_gap * font.em
            mark_to_base_gap = normalized_mark_to_base_gap * font.em
            depth_in_extrema = normalized_depth_in_extrema * font.em
            ignore_left_shift = normalized_ignore_left_shift * font.em
            ignore_right_shift = normalized_ignore_right_shift * font.em
            print('Processing glyphs...')
            for glyph in font.glyphs():
                if str(ff.scriptFromUnicode(glyph.unicode)) in ['arab','DFLT']:
                    list_of_y_max_extrema_points = []
                    list_of_y_min_extrema_points = []
                    full_on_curve_points_list = []
                    x_avarage_list_in_y_max = []
                    x_avarage_list_in_y_min = []
                    x_min = glyph.boundingBox()[0] ##bounding box tuple structure:(x_min,y_min,x_max,y_max)
                    x_max = glyph.boundingBox()[2]
                    glyph.preserveLayerAsUndo()
                    for ref in glyph.references:
                        glyph.unlinkRef()
                    glyph.addExtrema('all')
                    glyph.removeOverlap()
                    glyph.simplify()
                    contour_count = 0
                    for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
                        points = list(contour)
                        on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
                        max_extrema_point_in_y = max(on_curve_points_list, key=lambda x:x[1])
                        min_extrema_point_in_y = min(on_curve_points_list, key=lambda x:x[1])
                        for i in range(len(on_curve_points_list)):
                            full_on_curve_points_list.append(on_curve_points_list[i])
                        contour_count += 1
                    if contour_count == 0:
                        continue
                    y_max_extrema = max(full_on_curve_points_list, key=lambda x:x[1])
                    y_min_extrema = min(full_on_curve_points_list, key=lambda x:x[1])
    
                    for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
                        points = list(contour)
                        on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
                        for point in on_curve_points_list:
                            if point == y_max_extrema:
                                middle_x_point_of_topmost_contour = (max(on_curve_points_list)[0]+min(on_curve_points_list)[0])/2
                            elif point == y_min_extrema:
                                middle_x_point_of_bottommost_contour = (max(on_curve_points_list)[0]+min(on_curve_points_list)[0])/2
                    top_middle_of_topmost_contour = (middle_x_point_of_topmost_contour,y_max_extrema[1])
                    bottom_middle_of_bottommost_contour = (middle_x_point_of_bottommost_contour,y_min_extrema[1])
                    
                    contour_x_coords_list = []
                    contour_y_coords_list = []
                    for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
                        points = list(contour)
                        on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
                        for point in on_curve_points_list:
                            if point[1] >= y_max_extrema[1] - y_extrema_avarge_tolerance:
                                contour_x_coords_list.append(max(on_curve_points_list)[0])
                                contour_x_coords_list.append(min(on_curve_points_list)[0])
                                contour_y_coords_list.append(max(on_curve_points_list, key=lambda x:x[1])[1])
                    topmost_mid_x_point = (max(contour_x_coords_list)+min(contour_x_coords_list))/2
                    topmost_mid_y_point = sum(i for i in contour_y_coords_list)/len(contour_y_coords_list)
                    topmost_contours_mid_point = (topmost_mid_x_point,topmost_mid_y_point)
        
                    contour_x_coords_list = []
                    contour_y_coords_list = []
                    for contour in font[glyph.glyphname].layers[glyph.activeLayer]:
                        points = list(contour)
                        on_curve_points_list = [(points[i].x,points[i].y) for i in range(len(points)) if points[i].on_curve]
                        for point in on_curve_points_list:
                            if point[1] < y_min_extrema[1] + y_extrema_avarge_tolerance:
                                contour_x_coords_list.append(max(on_curve_points_list)[0])
                                contour_x_coords_list.append(min(on_curve_points_list)[0])
                                contour_y_coords_list.append(min(on_curve_points_list, key=lambda x:x[1])[1])
                    bottommost_mid_x_point = (max(contour_x_coords_list)+min(contour_x_coords_list))/2
                    bottommost_mid_y_point = sum(i for i in contour_y_coords_list)/len(contour_y_coords_list)
                    bottommost_contours_mid_point = (bottommost_mid_x_point,bottommost_mid_y_point)
                                
                    for point in full_on_curve_points_list:
                        if point[1] >= y_max_extrema[1] - y_extrema_avarge_tolerance:
                            x_avarage_list_in_y_max.append(point)
                        if point[1] < y_min_extrema[1] + y_extrema_avarge_tolerance:
                            x_avarage_list_in_y_min.append(point)                            
        
                    x_avarage_list_in_y_max = list(dict.fromkeys(x_avarage_list_in_y_max)) #remove duplicates
                    x_avarage_list_in_y_min = list(dict.fromkeys(x_avarage_list_in_y_min)) #remove duplicates
                    avarage_y_max_extrema = (sum(i[0] for i in x_avarage_list_in_y_max)/len(x_avarage_list_in_y_max),sum(i[1] for i in x_avarage_list_in_y_max)/len(x_avarage_list_in_y_max))
                    avarage_y_min_extrema = (sum(i[0] for i in x_avarage_list_in_y_min)/len(x_avarage_list_in_y_min),sum(i[1] for i in x_avarage_list_in_y_min)/len(x_avarage_list_in_y_min))
                    glyph.doUndoLayer()
        
                    if glyph.unicode in ligature_glyphs_dict:
                        font[glyph.unicode].glyphclass = "baseglyph"
                        print('-----------------ligature glyph:',glyph.glyphname)
                            #top:
                        if ligature_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top#0:extrema':
                            font[glyph.unicode].addAnchorPoint("top_lig","ligature",y_max_extrema_liga('double','first_part','avarage')[0],y_max_extrema_liga('double','first_part','avarage')[1],0)
                        if ligature_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'top#1:extrema':
                            font[glyph.unicode].addAnchorPoint("top_lig","ligature",y_max_extrema_liga('double','secound_part','avarage')[0],y_max_extrema_liga('double','secound_part','avarage')[1],1)
                        if ligature_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'top#1:topmost_contour_mid_point':
                            font[glyph.unicode].addAnchorPoint("top_lig","ligature",sidemost_contour_mid_point_liga('double','secound_part',glyph.unicode,'up')[0],sidemost_contour_mid_point_liga('double','secound_part',glyph.unicode,'up')[1],1)
                        if ligature_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top#0:topmost_contour_mid_point(closer)':
                            font[glyph.unicode].addAnchorPoint("top_lig","ligature",sidemost_contour_mid_point_liga('double','first_part',glyph.unicode,'up')[0],sidemost_contour_mid_point_liga('double','first_part',glyph.unicode,'up')[1]-depth_in_extrema,0)
                        if ligature_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'top#1:topmost_contour_mid_point(closer)':
                            font[glyph.unicode].addAnchorPoint("top_lig","ligature",sidemost_contour_mid_point_liga('double','secound_part',glyph.unicode,'up')[0],sidemost_contour_mid_point_liga('double','secound_part',glyph.unicode,'up')[1]-depth_in_extrema,1)
                            #bottom:
                        if ligature_glyphs_dict[glyph.unicode].rsplit('|')[2].replace('"','')== 'bottom#0:extrema':
                            font[glyph.unicode].addAnchorPoint("bottom_lig","ligature",y_max_extrema_liga('double','first_part','avarage')[0],y_min_extrema[1],0)
                        if ligature_glyphs_dict[glyph.unicode].rsplit('|')[3].replace('"','')== 'bottom#1:extrema':
                            font[glyph.unicode].addAnchorPoint("bottom_lig","ligature",y_max_extrema_liga('double','secound_part','avarage')[0],y_min_extrema[1],1)
                        if ligature_glyphs_dict[glyph.unicode].rsplit('|')[2].replace('"','')== 'bottom#0:bottommost_contour_mid_point':
                            font[glyph.unicode].addAnchorPoint("bottom_lig","ligature",sidemost_contour_mid_point_liga('double','first_part',glyph.unicode,'down')[0],sidemost_contour_mid_point_liga('double','first_part',glyph.unicode,'down')[1],0)
                        if ligature_glyphs_dict[glyph.unicode].rsplit('|')[3].replace('"','')== 'bottom#1:bottommost_contour_mid_point':
                            font[glyph.unicode].addAnchorPoint("bottom_lig","ligature",sidemost_contour_mid_point_liga('double','secound_part',glyph.unicode,'down')[0],sidemost_contour_mid_point_liga('double','secound_part',glyph.unicode,'down')[1],1)
                        if ligature_glyphs_dict[glyph.unicode].rsplit('|')[2].replace('"','')== 'bottom#0:bottommost_contour_mid_point(closer)':
                            font[glyph.unicode].addAnchorPoint("bottom_lig","ligature",sidemost_contour_mid_point_liga('double','first_part',glyph.unicode,'down')[0],sidemost_contour_mid_point_liga('double','first_part',glyph.unicode,'down')[1]+depth_in_extrema,0)
                        if ligature_glyphs_dict[glyph.unicode].rsplit('|')[3].replace('"','')== 'bottom#1:bottommost_contour_mid_point(closer)':
                            font[glyph.unicode].addAnchorPoint("bottom_lig","ligature",sidemost_contour_mid_point_liga('double','secound_part',glyph.unicode,'down')[0],sidemost_contour_mid_point_liga('double','secound_part',glyph.unicode,'down')[1]+depth_in_extrema,1)
                            
                    if glyph.glyphname in processed_non_Unicode_ligature_glyphs_dict:
                        font[glyph.glyphname].glyphclass = "baseglyph"
                        print('-----non-Unicode ligature glyph:',glyph.glyphname)
                            #top:
                        if processed_non_Unicode_ligature_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top#0:extrema':
                            font[glyph.glyphname].addAnchorPoint("top_lig","ligature",y_max_extrema_liga('double','first_part','avarage')[0],y_max_extrema_liga('double','first_part','avarage')[1],0)
                        if processed_non_Unicode_ligature_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'top#1:extrema':
                            font[glyph.glyphname].addAnchorPoint("top_lig","ligature",y_max_extrema_liga('double','secound_part','avarage')[0],y_max_extrema_liga('double','secound_part','avarage')[1],1)
                        if processed_non_Unicode_ligature_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'top#1:topmost_contour_mid_point':
                            font[glyph.glyphname].addAnchorPoint("top_lig","ligature",sidemost_contour_mid_point_liga('double','secound_part',glyph.glyphname,'up')[0],sidemost_contour_mid_point_liga('double','secound_part',glyph.glyphname,'up')[1],1)
                        if processed_non_Unicode_ligature_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top#0:topmost_contour_mid_point(closer)':
                            font[glyph.glyphname].addAnchorPoint("top_lig","ligature",sidemost_contour_mid_point_liga('double','first_part',glyph.glyphname,'up')[0],sidemost_contour_mid_point_liga('double','first_part',glyph.glyphname,'up')[1]-depth_in_extrema,0)
                        if processed_non_Unicode_ligature_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'top#1:topmost_contour_mid_point(closer)':
                            font[glyph.glyphname].addAnchorPoint("top_lig","ligature",sidemost_contour_mid_point_liga('double','secound_part',glyph.glyphname,'up')[0],sidemost_contour_mid_point_liga('double','secound_part',glyph.glyphname,'up')[1]-depth_in_extrema,1)
                            #bottom:
                        if processed_non_Unicode_ligature_glyphs_dict[glyph.glyphname].rsplit('|')[2].replace('"','')== 'bottom#0:extrema':
                            font[glyph.glyphname].addAnchorPoint("bottom_lig","ligature",y_max_extrema_liga('double','first_part','avarage')[0],y_min_extrema[1],0)
                        if processed_non_Unicode_ligature_glyphs_dict[glyph.glyphname].rsplit('|')[3].replace('"','')== 'bottom#1:extrema':
                            font[glyph.glyphname].addAnchorPoint("bottom_lig","ligature",y_max_extrema_liga('double','secound_part','avarage')[0],y_min_extrema[1],1)
                        if processed_non_Unicode_ligature_glyphs_dict[glyph.glyphname].rsplit('|')[2].replace('"','')== 'bottom#0:bottommost_contour_mid_point':
                            font[glyph.glyphname].addAnchorPoint("bottom_lig","ligature",sidemost_contour_mid_point_liga('double','first_part',glyph.glyphname,'down')[0],sidemost_contour_mid_point_liga('double','first_part',glyph.glyphname,'down')[1],0)
                        if processed_non_Unicode_ligature_glyphs_dict[glyph.glyphname].rsplit('|')[3].replace('"','')== 'bottom#1:bottommost_contour_mid_point':
                            font[glyph.glyphname].addAnchorPoint("bottom_lig","ligature",sidemost_contour_mid_point_liga('double','secound_part',glyph.glyphname,'down')[0],sidemost_contour_mid_point_liga('double','secound_part',glyph.glyphname,'down')[1],1)
                        if processed_non_Unicode_ligature_glyphs_dict[glyph.glyphname].rsplit('|')[2].replace('"','')== 'bottom#0:bottommost_contour_mid_point(closer)':
                            font[glyph.glyphname].addAnchorPoint("bottom_lig","ligature",sidemost_contour_mid_point_liga('double','first_part',glyph.glyphname,'down')[0],sidemost_contour_mid_point_liga('double','first_part',glyph.glyphname,'down')[1]+depth_in_extrema,0)
                        if processed_non_Unicode_ligature_glyphs_dict[glyph.glyphname].rsplit('|')[3].replace('"','')== 'bottom#1:bottommost_contour_mid_point(closer)':
                            font[glyph.glyphname].addAnchorPoint("bottom_lig","ligature",sidemost_contour_mid_point_liga('double','secound_part',glyph.glyphname,'down')[0],sidemost_contour_mid_point_liga('double','secound_part',glyph.glyphname,'down')[1]+depth_in_extrema,1)
  
                    elif glyph.unicode in base_glyphs_dict:
                        font[glyph.unicode].glyphclass = "baseglyph"
                        print('-------------Unicode base glyph:',glyph.glyphname)
                        #top:
                        if base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:extrema':
                            font[glyph.unicode].addAnchorPoint("top","base",y_max_extrema[0],y_max_extrema[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:avarage_extrema':
                            font[glyph.unicode].addAnchorPoint("top","base",avarage_y_max_extrema[0],avarage_y_max_extrema[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:mid':
                            font[glyph.unicode].addAnchorPoint("top","base",round((x_min+x_max)/2),y_max_extrema[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:topmost_contour_mid_point':
                            font[glyph.unicode].addAnchorPoint("top","base",sidemost_contour_mid_point(glyph.unicode,y_max_extrema),y_max_extrema[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:topmost_contour_mid_point(closer)':
                            font[glyph.unicode].addAnchorPoint("top","base",sidemost_contour_mid_point(glyph.unicode,y_max_extrema),y_max_extrema[1]-depth_in_extrema)
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:topmost_contours_mid_point':
                            font[glyph.unicode].addAnchorPoint("top","base",topmost_contours_mid_point[0],topmost_contours_mid_point[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:topmost_contours_mid_point(closer)':
                            font[glyph.unicode].addAnchorPoint("top","base",topmost_contours_mid_point[0],topmost_contours_mid_point[1]-depth_in_extrema)
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:avarage_topmost_contour_mid_point':
                            vertical_avarage_side_most_ = vertical_avarage_side_most(glyph.unicode,'up')
                            font[glyph.unicode].addAnchorPoint("top","base",vertical_avarage_side_most_[0],vertical_avarage_side_most_[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:avarage_topmost_contour_mid_point(closer)':
                            vertical_avarage_side_most_ = vertical_avarage_side_most(glyph.unicode,'up')
                            font[glyph.unicode].addAnchorPoint("top","base",vertical_avarage_side_most_[0],vertical_avarage_side_most_[1]-depth_in_extrema)
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:topmost_slope_mid':
                            font[glyph.unicode].addAnchorPoint("top","base",kaf_top_anchor_find(glyph.unicode)[0],y_max_extrema[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:kaf':
                            kaf_top_anchor_find_ = kaf_top_anchor_find(glyph.unicode)
                            font[glyph.unicode].addAnchorPoint("top","base",kaf_top_anchor_find_[0],kaf_top_anchor_find_[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:BIG_y_extrema':
                            BIG_y_extrema_ = BIG_y_extrema(glyph.boundingBox()[0],glyph.boundingBox()[2])
                            font[glyph.unicode].addAnchorPoint("top","base",BIG_y_extrema_[0],BIG_y_extrema_[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:BIG_y_extrema(after_x_bottom_extrema)':
                            BIG_y_extrema_ = BIG_y_extrema(y_min_extrema[0],glyph.boundingBox()[2])
                            font[glyph.unicode].addAnchorPoint("top","base",BIG_y_extrema_[0],BIG_y_extrema_[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:avarage_extrema_ignore_left':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.unicode,'ignore_left','y_max')
                            font[glyph.unicode].addAnchorPoint("top","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:avarage_extrema_ignore_right':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.unicode,'ignore_right','y_max')
                            font[glyph.unicode].addAnchorPoint("top","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:avarage_extrema_ignore_left(closer)':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.unicode,'ignore_left','y_max')
                            font[glyph.unicode].addAnchorPoint("top","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1]-depth_in_extrema)
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[0].replace('"','')== 'top:avarage_extrema_ignore_right(closer)':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.unicode,'ignore_right','y_max')
                            font[glyph.unicode].addAnchorPoint("top","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1]-depth_in_extrema)
                        #bottom:
                        if base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:extrema':
                            font[glyph.unicode].addAnchorPoint("bottom","base",y_min_extrema[0],y_min_extrema[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:avarage_extrema':
                            font[glyph.unicode].addAnchorPoint("bottom","base",avarage_y_min_extrema[0],avarage_y_min_extrema[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:avarage_extrema_center':
                            avarage_y_min_extrema_center_ = avarage_y_min_extrema_center(glyph.unicode)
                            font[glyph.unicode].addAnchorPoint("bottom","base",avarage_y_min_extrema_center_[0],avarage_y_min_extrema_center_[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:mid':
                            font[glyph.unicode].addAnchorPoint("bottom","base",round((x_min+x_max)/2),y_min_extrema[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:bottommost_contour_mid_point':
                            font[glyph.unicode].addAnchorPoint("bottom","base",sidemost_contour_mid_point(glyph.unicode,y_min_extrema),y_min_extrema[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:bottommost_contour_mid_point(closer)':
                            font[glyph.unicode].addAnchorPoint("bottom","base",sidemost_contour_mid_point(glyph.unicode,y_min_extrema),y_min_extrema[1]+depth_in_extrema)
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:bottommost_contours_mid_point':
                            font[glyph.unicode].addAnchorPoint("bottom","base",bottommost_contours_mid_point[0],bottommost_contours_mid_point[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:bottommost_contours_mid_point(closer)':
                            font[glyph.unicode].addAnchorPoint("bottom","base",bottommost_contours_mid_point[0],bottommost_contours_mid_point[1]+depth_in_extrema)
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:avarage_bottommost_contour_mid_point':
                            vertical_avarage_side_most_ = vertical_avarage_side_most(glyph.unicode,'down')
                            font[glyph.unicode].addAnchorPoint("bottom","base",vertical_avarage_side_most_[0],vertical_avarage_side_most_[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:avarage_bottommost_contour_mid_point(closer)':
                            vertical_avarage_side_most_ = vertical_avarage_side_most(glyph.unicode,'down')
                            font[glyph.unicode].addAnchorPoint("bottom","base",vertical_avarage_side_most_[0],vertical_avarage_side_most_[1]+depth_in_extrema)
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:avarage_extrema_ignore_left':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.unicode,'ignore_left','y_min')
                            font[glyph.unicode].addAnchorPoint("bottom","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:avarage_extrema_ignore_left_center':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.unicode,'ignore_left_center','y_min')
                            font[glyph.unicode].addAnchorPoint("bottom","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:avarage_extrema_ignore_right':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.unicode,'ignore_right','y_min')
                            font[glyph.unicode].addAnchorPoint("bottom","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1])
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:avarage_extrema_ignore_left(closer)':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.unicode,'ignore_left','y_min')
                            font[glyph.unicode].addAnchorPoint("bottom","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1]-depth_in_extrema)
                        elif base_glyphs_dict[glyph.unicode].rsplit('|')[1].replace('"','')== 'bottom:avarage_extrema_ignore_right(closer)':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.unicode,'ignore_right','y_min')
                            font[glyph.unicode].addAnchorPoint("bottom","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1]-depth_in_extrema)
                            
                    elif glyph.glyphname in non_Unicode_base_glyphs_dict:
                        font[glyph.glyphname].glyphclass = "baseglyph"
                        print('---------non-Unicode base glyph:',glyph.glyphname)
                        #top:
                        if non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:extrema':
                            font[glyph.glyphname].addAnchorPoint("top","base",y_max_extrema[0],y_max_extrema[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:avarage_extrema':
                            font[glyph.glyphname].addAnchorPoint("top","base",avarage_y_max_extrema[0],avarage_y_max_extrema[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:mid':
                            font[glyph.glyphname].addAnchorPoint("top","base",round((x_min+x_max)/2),y_max_extrema[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:topmost_contour_mid_point':
                            font[glyph.glyphname].addAnchorPoint("top","base",sidemost_contour_mid_point(glyph.glyphname,y_max_extrema),y_max_extrema[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:topmost_contour_mid_point(closer)':
                            font[glyph.glyphname].addAnchorPoint("top","base",sidemost_contour_mid_point(glyph.glyphname,y_max_extrema),y_max_extrema[1]-depth_in_extrema)
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:topmost_contours_mid_point':
                            font[glyph.glyphname].addAnchorPoint("top","base",topmost_contours_mid_point[0],topmost_contours_mid_point[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:topmost_contours_mid_point(closer)':
                            font[glyph.glyphname].addAnchorPoint("top","base",topmost_contours_mid_point[0],topmost_contours_mid_point[1]-depth_in_extrema)
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:avarage_topmost_contour_mid_point':
                            vertical_avarage_side_most_ = vertical_avarage_side_most(glyph.glyphname,'up')
                            font[glyph.glyphname].addAnchorPoint("top","base",vertical_avarage_side_most_[0],vertical_avarage_side_most_[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:avarage_topmost_contour_mid_point(closer)':
                            vertical_avarage_side_most_ = vertical_avarage_side_most(glyph.glyphname,'up')
                            font[glyph.glyphname].addAnchorPoint("top","base",vertical_avarage_side_most_[0],vertical_avarage_side_most_[1]-depth_in_extrema)
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:topmost_slope_mid':
                            font[glyph.glyphname].addAnchorPoint("top","base",kaf_top_anchor_find(glyph.glyphname)[0],y_max_extrema[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:kaf':
                            kaf_top_anchor_find_ = kaf_top_anchor_find(glyph.glyphname)
                            font[glyph.glyphname].addAnchorPoint("top","base",kaf_top_anchor_find_[0],kaf_top_anchor_find_[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:BIG_y_extrema':
                            BIG_y_extrema_ = BIG_y_extrema(glyph.boundingBox()[0],glyph.boundingBox()[2])
                            font[glyph.glyphname].addAnchorPoint("top","base",BIG_y_extrema_[0],BIG_y_extrema_[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:BIG_y_extrema(after_x_bottom_extrema)':
                            BIG_y_extrema_ = BIG_y_extrema(y_min_extrema[0],glyph.boundingBox()[2])
                            font[glyph.glyphname].addAnchorPoint("top","base",BIG_y_extrema_[0],BIG_y_extrema_[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:avarage_extrema_ignore_left':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.glyphname,'ignore_left','y_max')
                            font[glyph.glyphname].addAnchorPoint("top","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:avarage_extrema_ignore_right':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.glyphname,'ignore_right','y_max')
                            font[glyph.glyphname].addAnchorPoint("top","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:avarage_extrema_ignore_left(closer)':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.glyphname,'ignore_left','y_max')
                            font[glyph.glyphname].addAnchorPoint("top","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1]-depth_in_extrema)
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[0].replace('"','')== 'top:avarage_extrema_ignore_right(closer)':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.glyphname,'ignore_right','y_max')
                            font[glyph.glyphname].addAnchorPoint("top","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1]-depth_in_extrema)
                        #bottom:
                        if non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:extrema':
                            font[glyph.glyphname].addAnchorPoint("bottom","base",y_min_extrema[0],y_min_extrema[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:avarage_extrema':
                            font[glyph.glyphname].addAnchorPoint("bottom","base",avarage_y_min_extrema[0],avarage_y_min_extrema[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:avarage_extrema_center':
                            avarage_y_min_extrema_center_ = avarage_y_min_extrema_center(glyph.glyphname)
                            font[glyph.glyphname].addAnchorPoint("bottom","base",avarage_y_min_extrema_center_[0],avarage_y_min_extrema_center_[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:mid':
                            font[glyph.glyphname].addAnchorPoint("bottom","base",round((x_min+x_max)/2),y_min_extrema[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:bottommost_contour_mid_point':
                            font[glyph.glyphname].addAnchorPoint("bottom","base",sidemost_contour_mid_point(glyph.glyphname,y_min_extrema),y_min_extrema[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:bottommost_contour_mid_point(closer)':
                            font[glyph.glyphname].addAnchorPoint("bottom","base",sidemost_contour_mid_point(glyph.glyphname,y_min_extrema),y_min_extrema[1]+depth_in_extrema)
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:bottommost_contours_mid_point':
                            font[glyph.glyphname].addAnchorPoint("bottom","base",bottommost_contours_mid_point[0],bottommost_contours_mid_point[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:bottommost_contours_mid_point(closer)':
                            font[glyph.glyphname].addAnchorPoint("bottom","base",bottommost_contours_mid_point[0],bottommost_contours_mid_point[1]+depth_in_extrema)
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:avarage_bottommost_contour_mid_point':
                            vertical_avarage_side_most_ = vertical_avarage_side_most(glyph.glyphname,'down')
                            font[glyph.glyphname].addAnchorPoint("bottom","base",vertical_avarage_side_most_[0],vertical_avarage_side_most_[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:avarage_bottommost_contour_mid_point(closer)':
                            vertical_avarage_side_most_ = vertical_avarage_side_most(glyph.glyphname,'down')
                            font[glyph.glyphname].addAnchorPoint("bottom","base",vertical_avarage_side_most_[0],vertical_avarage_side_most_[1]+depth_in_extrema)
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:avarage_extrema_ignore_left':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.glyphname,'ignore_left','y_min')
                            font[glyph.glyphname].addAnchorPoint("bottom","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:avarage_extrema_ignore_left_center':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.glyphname,'ignore_left_center','y_min')
                            font[glyph.glyphname].addAnchorPoint("bottom","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:avarage_extrema_ignore_right':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.glyphname,'ignore_right','y_min')
                            font[glyph.glyphname].addAnchorPoint("bottom","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1])
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:avarage_extrema_ignore_left(closer)':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.glyphname,'ignore_left','y_min')
                            font[glyph.glyphname].addAnchorPoint("bottom","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1]-depth_in_extrema)
                        elif non_Unicode_base_glyphs_dict[glyph.glyphname].rsplit('|')[1].replace('"','')== 'bottom:avarage_extrema_ignore_right(closer)':
                            y_extrema_ignore_side_ = y_extrema_ignore_side(glyph.glyphname,'ignore_right','y_min')
                            font[glyph.glyphname].addAnchorPoint("bottom","base",y_extrema_ignore_side_[0],y_extrema_ignore_side_[1]-depth_in_extrema)
                            
                    elif glyph.unicode in top_mark_glyphs:
                        print('---------Unicode top mark glyph:',glyph.glyphname)
                        font[glyph.unicode].glyphclass = "mark"
                        font[glyph.unicode].addAnchorPoint("top_mark","basemark",round((x_min+x_max)/2),glyph.boundingBox()[3] + mark_to_base_gap)
                        font[glyph.unicode].addAnchorPoint("top_mark","mark",round((x_min+x_max)/2),glyph.boundingBox()[1] + mark_to_mark_gap)
                        # font[glyph.unicode].addAnchorPoint("top_mark","mark",round((x_min+x_max)/2),glyph_bbox_bottom_mid_first_inShape_point(glyph.unicode) + mark_to_mark_gap)
                        font[glyph.unicode].addAnchorPoint("top","mark",round((x_min+x_max)/2),glyph.boundingBox()[1] - mark_to_base_gap)
                        font[glyph.unicode].addAnchorPoint("top_lig","mark",round((x_min+x_max)/2),glyph.boundingBox()[1] - mark_to_base_gap)
            
                    elif glyph.unicode in bottom_mark_glyphs:
                        print('------Unicode bottom mark glyph:',glyph.glyphname)
                        font[glyph.unicode].glyphclass = "mark"
                        font[glyph.unicode].addAnchorPoint("bottom_mark","basemark",round((x_min+x_max)/2),glyph.boundingBox()[1] - mark_to_base_gap)
                        font[glyph.unicode].addAnchorPoint("bottom_mark","mark",round((x_min+x_max)/2),glyph.boundingBox()[3] - mark_to_mark_gap)
                        font[glyph.unicode].addAnchorPoint("bottom","mark",round((x_min+x_max)/2),glyph.boundingBox()[3] + mark_to_base_gap)
                        font[glyph.unicode].addAnchorPoint("bottom_lig","mark",round((x_min+x_max)/2),glyph.boundingBox()[3] + mark_to_base_gap)
                        
                    elif glyph.glyphname in top_ligature_mark_glyphs:
                        print('--------top ligature mark glyph:',glyph.glyphname)
                        font[glyph.glyphname].glyphclass = "mark"
                        font[glyph.glyphname].addAnchorPoint("top_mark","basemark",round((x_min+x_max)/2),glyph.boundingBox()[3] + mark_to_base_gap)
                        font[glyph.glyphname].addAnchorPoint("top_mark","mark",round((x_min+x_max)/2),glyph.boundingBox()[1] + mark_to_mark_gap)
                        font[glyph.glyphname].addAnchorPoint("top","mark",round((x_min+x_max)/2),glyph.boundingBox()[1] - mark_to_base_gap)
                        font[glyph.glyphname].addAnchorPoint("top_lig","mark",round((x_min+x_max)/2),glyph.boundingBox()[1] - mark_to_base_gap)
                        
                    elif glyph.glyphname in bottom_ligature_mark_glyphs:
                        print('-----bottom ligature mark glyph:',glyph.glyphname)
                        font[glyph.glyphname].glyphclass = "mark"
                        font[glyph.glyphname].addAnchorPoint("bottom_mark","basemark",round((x_min+x_max)/2),glyph.boundingBox()[1] - mark_to_base_gap)
                        font[glyph.glyphname].addAnchorPoint("bottom_mark","mark",round((x_min+x_max)/2),glyph.boundingBox()[3] - mark_to_mark_gap)
                        font[glyph.glyphname].addAnchorPoint("bottom","mark",round((x_min+x_max)/2),glyph.boundingBox()[3] + mark_to_base_gap)
                        font[glyph.glyphname].addAnchorPoint("bottom_lig","mark",round((x_min+x_max)/2),glyph.boundingBox()[3] + mark_to_base_gap)
            if os.path.split(args.output_file)[0]:
                os.chdir(os.path.split(args.output_file)[0])
            input_file = os.path.split(args.input_file)[1]
            output_file = os.path.split(args.output_file)[1]
            if output_file[-3:] == "sfd":
                if output_file == input_file:
                    output_name = output_file[:-4] + "-AutoMark" + output_file[-4:]
                else:
                    output_name = output_file
                print('saving font...')
                font.save(output_name)
            else:
                if output_file == input_file:
                    output_name = output_file[:-4] + "-AutoMark" + output_file[-4:]
                else:
                    output_name = output_file
                print('generating font...')
                font.generate(output_name)
            print('Done!')
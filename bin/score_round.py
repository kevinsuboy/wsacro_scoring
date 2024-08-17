#!/usr/bin/env python
import argparse
import Convert
import os
import KeyLog as kl
import pandas as pd
import numpy as np
import code
import math
from datetime import timedelta as td

def parse_cmdline(parser=None):
    if not parser:
        parser = argparse.ArgumentParser(
            prog='score_round.py',
            description='',
            epilog=''
        )
    parser.add_argument('-c', '--convert',action="store_true",help='') 
    parser.add_argument('-s', '--score',action="store_true",help='') 
    parser.add_argument('-re', '--render',action="store_true",help='') 
    parser.add_argument('-r', '--round_list',action="store",help='',required=True) 
    parser.add_argument('-sid', '--score_id',action="store",help='') 
    parser.add_argument('-t', '--team',action="store",help='') 
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_cmdline()
    sid = args.score_id if args.score_id else None
    os.system("sed -i 's/ //g' %s"%(args.round_list))
    df = pd.read_csv(args.round_list)
    top = {}
    rnd = {}
    scores = {}
    freelist = {}
    total = {}
    norm = {}
    for idx,el in df.iterrows():
        os.makedirs("%d_scored"%(el['roundN']),exist_ok=True)
        ires = str(el["ires"]) if not pd.isnull(el["ires"]) else "720"
        ores = str(el["ores"]) if not pd.isnull(el["ores"]) else "720"
        # code.interact(local=locals())
        obj = Convert.Convert(el["flysight"],el["fver"],el["slate"],el["comp"],el["output"],el["mp4"],str(el['roundN']),(ires,ores), el["seq"])
        rnd[str(el["roundN"]),el["output"]] = (obj,el["rtype"],obj.comp_time)
        top[str(el["roundN"])+"_scored"] = {
        "docks": 0,
        "style": 0,
        "dive_plan": 0,
        "camera": 0
        }
        if args.convert and (not args.team or el["output"] == args.team):
            obj.convert_format()
    big_dock_list = {}

    iso_list = [[rn,el] for rn,el in rnd.keys() if el == args.team] if args.team else rnd.keys()
    # code.interact(local=locals())
    for fout_dir,fout in iso_list:
        obj,rtype,comp_time = rnd[(fout_dir,fout)]
        # code.interact(local=locals())
        fout_dir += "_scored"
        if args.score:
            if not args.score_id:
                print("ERROR: need an sid")
                quit()
            _ = (kl.KeyLog("%s/_%s_%s.scores"%(fout_dir,fout,sid),rtype).run("%s/__%s_tmp__.mp4"%(fout_dir,fout)))
        if args.render:
            flist = list(filter(None, os.popen("ls %s/_%s_*.scores"%(fout_dir,fout)).read().split('\n')))
            total[(fout_dir,fout)] = {
                "type": rtype,
                }
            style = []
            dive_plan = []
            camera = []
            judges = []
            dock_list = pd.DataFrame()
            time_list = pd.DataFrame()
            final_score = pd.DataFrame()
            for file in flist:
                thisID = file.split('/')[-1].split('.scores')[0].split('_')[-1]
                df = pd.read_csv(file)
                df['time_delta'] = pd.to_timedelta(df['time_delta'],unit='s')
                # code.interact(local=locals())
                df = df[(comp_time - df['time_delta'] >= td(seconds=0)) | (df['style'].notnull())]
                df = df.replace('<96>',"'0'")
                if rtype == 'C':
                    data = df['key'][df['key'].notnull()]
                    dock_list[thisID] = data
                    data = df['time_delta'][df['time_delta'].notnull()]
                    time_list[thisID] = data
                cq = df['camera_quality'][df['camera_quality'].notnull()].iloc[-1] if 'camera_quality' in df else 0
                cp = df['camera_prog'][df['camera_prog'].notnull()].iloc[-1] if 'camera_prog' in df else 0
                style.append( df['style'][df['style'].notnull()].iloc[-1])
                dive_plan.append( df['dive_plan'][df['dive_plan'].notnull()].iloc[-1] if 'dive_plan' in df else 0)
                camera.append([ cq , cp ])
                judges.append(thisID)

            if rtype == 'C':
                final_score['key'] = dock_list.mode(axis=1)[0]
                final_score['time_delta'] = time_list.mean(axis=1)
                final_score['comments'] = df['comments']
                final_score['style'] = df['style']
                final_score['dive_plan'] = df['dive_plan'] if 'dive_plan' in df else np.NaN
                final_score['camera'] = np.NaN
            # code.interact(local=locals())
            total[(fout_dir,fout)]["docks"] = final_score['key'][final_score['key']=="'+'"].count() if rtype == 'C' else 0
            total[(fout_dir,fout)]["style"] = round(sum(style)/len(style),1)
            total[(fout_dir,fout)]["dive_plan"] = round(sum(dive_plan)/len(dive_plan),1)
            total[(fout_dir,fout)]["camera"] = round(sum([sum(el) for el in camera])/len(camera),1)
            final_score = final_score.append({
                                            'key': np.NaN,
                                            'time_delta': td(seconds=0),
                                            'comments': np.NaN,
                                            'style':total[(fout_dir,fout)]["style"],
                                            'dive_plan':total[(fout_dir,fout)]["dive_plan"],
                                            'camera':total[(fout_dir,fout)]["camera"]
                                            },
                                            ignore_index=True)
            final_score.to_csv("%s/_final_%s.scores"%(fout_dir,fout))
            scores[(fout_dir,fout)] = final_score[final_score["time_delta"].notnull()].values.tolist() 
            freelist[(fout_dir,fout)] = {
                "judges" : judges,
                "style" : style,
                "dive_plan" : dive_plan,
                "camera" : camera
            }
            for k in [k for k in top[fout_dir].keys() if total[(fout_dir,fout)][k] > top[fout_dir][k]]:
                top[fout_dir][k] = total[(fout_dir,fout)][k]
            big_dock_list[(fout_dir,fout)] = dock_list[dock_list.isin(["'+'","'-'","'0'","'*'"])].dropna()
    for rn,fout in total:
        rtype = total[rn,fout]["type"]
        # code.interact(local=locals())
        for k in [k for k in top[rn].keys() if total[rn,fout][k]>0]:
            if not (rn,fout) in norm:
                norm[rn,fout] = {}
            norm[rn,fout][k] = total[rn,fout][k]/top[rn][k]
            norm[rn,fout][k] *= 150 if rtype == "C" else 100
    with open("%s.out"%(args.round_list.split('.')[0]), 'w+') as f:
        for rn,fout in sorted(norm):
            f.write("%s %s: %d\n"%(rn,fout,sum(norm[rn,fout].values())))
    # iso_list = [[rn,el] for rn,el in scores.keys() if el == args.team] if args.team else scores.keys()
    # iso_list = [(el0+"_scored",el1) for el0,el1 in iso_list]
    # for fout_dir,fout in iso_list:
    #     print(scores[fout_dir+"_scored",fout])
    #     print(big_dock_list[fout_dir+"_scored",fout].T)
    #     print(freelist[fout_dir+"_scored",fout])
    # code.interact(local=locals())
    if args.render:
        for fout_dir,fout in iso_list:
            cobj,rtype,comp_time = rnd[fout_dir,fout]
            cobj.get_start()
        # code.interact(local=locals())
        for fout_dir,fout in iso_list:
            cobj,rtype,comp_time = rnd[fout_dir,fout]
            cobj.save_video(scores[fout_dir+"_scored",fout],rtype,big_dock_list[fout_dir+"_scored",fout].T,freelist[fout_dir+"_scored",fout])
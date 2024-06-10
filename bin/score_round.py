#!/usr/bin/env python
import argparse
import Convert
import os
import KeyLog as kl
import pandas as pd
import numpy as np
import code
import math

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
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_cmdline()
    sid = args.score_id if args.score_id else 0
    df = pd.read_csv(args.round_list)
    cl = {}
    scores = {}
    total = {}
    norm = {}
    top = {
        "docks": 0,
        "style": 0,
        "dive_plan": 0,
        "camera": 0
        }
    for idx,el in df.iterrows():
        # code.interact(local=locals())
        obj = Convert.Convert(el["flysight"],el["fver"],el["slate"],el["comp"],el["output"],el["mp4"])
        cl[el["output"]] = (obj,el["rtype"])
        if args.convert:
            obj.convert_format()
    for el_out in cl.keys():
        obj,rtype = cl[el_out]
        tmp = el_out.split('/')
        fout_dir = '/'.join(tmp[0:-1])
        fout = tmp[-1]
        if args.score:
            _ = (kl.KeyLog("%s/_%s_%d.scores"%(fout_dir,fout,sid),rtype).run("%s/__%s_tmp__.mp4"%(fout_dir,fout)))
        if args.render:
            flist = list(filter(None, os.popen("ls %s/_%s_*.scores"%(fout_dir,fout)).read().split('\n')))
            total[el_out] = {
                "type": rtype,
                }
            style = []
            dive_plan = []
            camera = {}
            dock_list = pd.DataFrame()
            time_list = pd.DataFrame()
            final_score = pd.DataFrame()
            for file in flist:
                thisID = int(file.split('/')[-1].split('.scores')[0].split('_')[-1])
                df = pd.read_csv(file)
                df['time_delta'] = pd.to_timedelta(df['time_delta'],unit='s')
                # code.interact(local=locals())
                if rtype == 'C':
                    data = df['key'][df['key'].notnull()]
                    dock_list[thisID] = data
                    data = df['time_delta'][df['time_delta'].notnull()]
                    time_list[thisID] = data
                cq = df['camera_quality'][df['camera_quality'].notnull()].iloc[-1] if 'camera_quality' in df else 0
                cp = df['camera_prog'][df['camera_prog'].notnull()].iloc[-1] if 'camera_prog' in df else 0
                style.append( df['style'][df['style'].notnull()].iloc[-1])
                dive_plan.append( df['dive_plan'][df['dive_plan'].notnull()].iloc[-1] if 'dive_plan' in df else 0)
                camera[file] = ( cq , cp )

            if rtype == 'C':
                final_score['key'] = np.where( dock_list[dock_list == "'+'"].count(axis=1) > len(dock_list.columns)/2,"'+'","'-'")
                final_score['time_delta'] = time_list.mean(axis=1)
                final_score['comments'] = df['comments']
                final_score['style'] = df['style']
                final_score['dive_plan'] = df['dive_plan'] if 'dive_plan' in df else np.NaN
                final_score['camera'] = np.NaN
            total[el_out]["docks"] = final_score['key'][final_score['key']=="'+'"].count() if rtype == 'C' else 0
            total[el_out]["style"] = round(sum(style)/len(style),1)
            total[el_out]["dive_plan"] = round(sum(dive_plan)/len(dive_plan),1)
            total[el_out]["camera"] = round(sum([sum(el) for el in camera.values()])/len(camera),1)
            final_score = final_score.append({
                                            'key': np.NaN,
                                            'time_delta': np.NaN,
                                            'comments': np.NaN,
                                            'style':total[el_out]["style"],
                                            'dive_plan':total[el_out]["dive_plan"],
                                            'camera':total[el_out]["camera"]
                                            },
                                            ignore_index=True)
            final_score.to_csv("%s/_final_%s.scores"%(fout_dir,fout))
            scores[el_out] = final_score.values.tolist() 
            for k in [k for k in top.keys() if total[el_out][k] > top[k]]:
                top[k] = total[el_out][k]
    # code.interact(local=locals())
    for el_out in total:
        rtype = total[el_out]["type"]
        for k in [k for k in top.keys() if total[el_out][k]>0]:
            if not el_out in norm:
                norm[el_out] = {}
            norm[el_out][k] = total[el_out][k]/top[k]
            norm[el_out][k] *= 150 if rtype == "C" else 100
    with open("%s.out"%(args.round_list.split('.')[0]), 'w+') as f:
        for el_out in norm:
            f.write("%s: %d\n"%(el_out,sum(norm[el_out].values())))
    # code.interact(local=locals())
    if args.render:
        for el_out in cl.keys():
            cobj,rtype = cl[el_out]
            cobj.get_start()
        for el_out in cl.keys():
            cobj,rtype = cl[el_out]
            cobj.save_video(scores[el_out],rtype)
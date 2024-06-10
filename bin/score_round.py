#!/usr/bin/env python
import argparse
import Convert
import os
import KeyLog as kl
import pandas as pd
import code

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
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_cmdline()
    df = pd.read_csv(args.round_list)
    cl = {}
    scores = {}
    total = {}
    norm = {}
    top = {
        "docks": 0,
        "style": 0,
        "dive_plan": 0,
        "camera_quality": 0,
        "camera_prog":0 
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
            # code.interact(local=locals())
            _ = (kl.KeyLog("%s.scores"%(el_out),rtype).run("%s/__%s_tmp__.mp4"%(fout_dir,fout)))
        if args.render:
            df = pd.read_csv("%s.scores"%(el_out))
            df['time_delta'] = pd.to_timedelta(df['time_delta'],unit='s')
            scores[el_out] = df.values.tolist()
            # code.interact(local=locals())
            total[el_out] = {
                "type": rtype,
                "docks": df['key'][df['key']=="'+'"].count() if rtype == 'C' else 0,
                "style": df['style'][df['style'].notnull()].iloc[-1],
                "dive_plan": df['dive_plan'][df['dive_plan'].notnull()].iloc[-1] if 'dive_plan' in df else 0,
                "camera_quality": df['camera_quality'][df['camera_quality'].notnull()].iloc[-1] if 'camera_quality' in df else 0,
                "camera_prog": df['camera_prog'][df['camera_prog'].notnull()].iloc[-1] if 'camera_prog' in df else 0
                }
            for k in [k for k in top.keys() if total[el_out][k] > top[k]]:
                top[k] = total[el_out][k]
    for el_out in total:
        rtype = total[el_out]["type"]
        for k in [k for k in top.keys() if total[el_out][k]>0]:
            if not el_out in norm:
                norm[el_out] = {}
            norm[el_out][k] = total[el_out][k]/top[k]
            norm[el_out][k] *= 150 if rtype == "C" else 100
    # code.interact(local=locals())

    if args.render:
        for el_out in cl.keys():
            cobj,rtype = cl[el_out]
            cobj.get_start()
        for el_out in cl.keys():
            cobj,rtype = cl[el_out]
            cobj.save_video(scores[el_out],rtype)
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
    for idx,el in df.iterrows():
        # code.interact(local=locals())
        obj = Convert.Convert(el["flysight"],el["fver"],el["slate"],el["comp"],el["output"],el["mp4"])
        cl[el["output"]] = obj
        if args.convert:
            obj.convert_format()
    for el_out in cl.keys():
        if args.score:
            # code.interact(local=locals())
            _ = (kl.KeyLog("%s.scores"%(el_out)).run("__%s_tmp__.mp4"%(el_out)))
        df = pd.read_csv("%s.scores"%(el_out))
        df['time_delta'] = pd.to_timedelta(df['time_delta'],unit='s')
        scores[el_out] = df.values.tolist()
    # code.interact(local=locals())
    for el_out in cl.keys():
        if args.render:
            cl[el_out].get_start()
            cl[el_out].save_video(scores[el_out])
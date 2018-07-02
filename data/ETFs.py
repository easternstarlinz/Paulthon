import pandas as pd
import itertools

ETFs =  {
            'Large Cap'             :['SPY','IVV','VOO','IWB'],
            'Mid Cap'               :['MDY','IJH','VO','IWR'],
            'Small Cap'             :['IWM','IJR','VB'],
            'Global Equity'         :['VEU','ACWI','VXUS','DGT'],
            'AsiaPac Equity'        :['EWT','EWY','EWA','EWS','AAXJ','FXI','EWH','EWM','EPI','INDA','RSX'],
            'Europe Equity'         :['FEZ','EZU','VGK','HEDJ','EWU','EWI','EWP','EWQ','EWL','EWD'],
            'Emerging | Frontier'   :['EWZ','EWW','ECH','GAF','FM','EEM','VWO'],
            'Real Estate'           :['RWO','RWX','RWR','IYR','VNQ'],
            'Consumer Discretionary':['XLY','XRT','FXD','VCR','RTH','IYC'],
            'Consumer Staples'      :['XLP','FXG','VDC','ECON','IYK'],
            'Energy'                :['XLE','IPW','XOP','VDE','IYE','IXC','OIH'],
            'Financials'            :['XLF','KBE','KIE','IYG','KRE'],
            'Healthcare'            :['XLV','XBI','IBB'],
            'Industrial'            :['XLI','IYT','VIS','IYJ'],
            'Materials'             :['XLB','XHB','XME','IGE','MOO','LIT','GUNR'],
            'Technology'            :['XLK','SMH','HACK','FDN'],
            'Telecom'               :['IYZ','IXP','VOX'],
            'Utilities'             :['IDU','XLU','VPU'],
            'Oil | Gas'             :['UNG','BNO','OIL'],
            'Precious Metals'       :['GLD','SLV','IAU'],
            'Bonds'                 :['BND','AGG','JNK','LQD'],
            'T-Bond'                :['TLT','IEF','IEI','SHY','BIL','MINT'],
            'Precious Metals Miners':['SIL','GDX','GDXJ','PLTM']
        }

indices = ['QQQ']
for sector in ETFs.keys():
    indices.extend(ETFs[sector])
indices = sorted([i for i in indices if i not in  ('IPW', 'PLTM', 'GAF')])

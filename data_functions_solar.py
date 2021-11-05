import pvlib
import pymysql
import numpy as np
import pandas as pd



class Data:
    
    def __init__(self):
        print('Start: Data\n')
    
    
    def _print_start(self, content):
        print(f'Start: {content}')
    
    
    def _print_end(self, content):
        print(f'End: {content}\n')
    
    
    def _load_table(self, table, sql):
        content = f'Load {table}'
        self._print_start(content)
        db = pymysql.connect(user    = "사용자",\
                             passwd  = "비번",\
                             host    = "192.168.xx.xxx",\
                             db      = "db명",\
                             charset = "utf8",\
                             port    = 포트번호)
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute(sql)
        result = pd.DataFrame(cursor.fetchall())
        db.close()
        self._print_end(content)
        self.df = result.copy()
    
    
    # 위치 설정
    def _set_location(self, altitude = 0):
        # altitude = 0
        self.lat = float(self.df['LAT'].values)
        self.lon = float(self.df['LON'].values)
        return pvlib.location.Location(self.lat, self.lon, altitude = altitude)
    
    
    # 태양위치 데이터
    def load_solar_elev(self, site_id, times, tz = 'Asia/Seoul'):
        # site_id = 40009
        # times   = datetime type
        # tz      = Asia/Seoul
        
        self._load_site(site_id)
        loc = self._set_location()
        elv = loc.get_solarposition(times.tz_localize(tz))[['elevation', 'zenith', 'azimuth']]
        elv.index = elv.index.tz_localize(None)
        return elv
        
    
    # 청천일사량 데이터
    def load_clearsky(self, site_id, times, model, tz = 'Asia/Seoul', linke_turbidity = False):
        # site_id         = 40009
        # times           = datetime type
        # model           = ineichen, haurwitz
        # tz              = Asia/Seoul
        # linke_turbidity = True, False
        
        self._load_site(site_id)
        loc       = self._set_location()
        loc_times = times.tz_localize(tz)
        
        if   model == 'haurwitz':
            rad = loc.get_clearsky(loc_times, model = model)
        
        elif model == 'ineichen':
            if linke_turbidity:     # 링케혼탁도 월 평균값으로 설정
                rad = loc.get_clearsky(loc_times, model = model,
                                       linke_turbidity = pvlib.clearsky.lookup_linke_turbidity(loc_times, self.lat, self.lon))
            if not linke_turbidity: # 링케혼탁도 1(아주 맑음)으로 설정
                rad = loc.get_clearsky(loc_times, model = model, linke_turbidity = 1)
        
        rad.index = rad.index.tz_localize(None)
        return rad
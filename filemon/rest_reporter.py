import json
from filemon.graph import DataPlot
import requests


class RestReporter(DataPlot):
    
    def set_rest_server_ip(self, hostname, port,
                           post_url="api/files/{}"):
        self._hostname=hostname
        self._port=port
        self._post_url=post_url
        
    def get_url(self, file_id):
        rest_id=file_id
        if self._dict_of_rest_ids and file_id in self._dict_of_rest_ids.keys():
            rest_id=self._dict_of_rest_ids[file_id]
        return "http://{}:{}/{}".format(self._hostname,
                                        self._port,
                                        self._post_url.format(rest_id))
    
    def set_files_rest_ids(self, dict_of_rest_ids):
        self._dict_of_rest_ids=dict_of_rest_ids

    def do_other_actions(self, data_dict):  
        test_value=getattr(self, "_index_dict", None)
        if test_value is None:
            self._index_dict={x:0 for x in data_dict.keys()}
        for data_id, data_list in data_dict.items():
            index=self._index_dict[data_id]
            if index<len(data_list["time_stamps"]):
                for i in range(index, len(data_list["time_stamps"])):
                    time_stamp=data_list["time_stamps"][i]
                    file_size=data_list["file_sizes"][i]
                    file_percent=data_list["file_percents"][i]
                    throughput=data_list["throughputs"][i]
                    
                    result=self.send_report(data_id,  time_stamp,
                                    file_size, file_percent, throughput)
                    if result:
                        self._index_dict[data_id]+=1
                    else:
                        break
                
    def send_report(self, file_id, time_stamp,
                    file_size, file_percent, throughput):
        post_url=self.get_url(file_id)
        """{"timestamp":1508278312.707418,
        "received":13425,"completion":0.0008456109108939628,
        "rate":13288.663254459878}"""
        
        data_dict=dict(timestamp=time_stamp,
                       received=file_size,
                       completion=file_percent,
                       rate=throughput)
        try:
            results = requests.put(post_url, json=data_dict)
        except requests.exceptions.RequestException:
            return False
        if results.status_code==200:
            return True
        else: 
            return False
from datetime import timedelta
import re


class SRTHandler:
    def __init__(self,srt_file=None):
        self.srt_data = open(srt_file,"r").read()
        self.subtitle_list = sorted(self.set_timestamps(),key=lambda x:x.get("start")) 
    def _convert_to_timdelta(self,time_str):
        time_str = re.sub(r"[:,]"," ",time_str)
        h,m,s,ms = time_str.split(" ")
        return timedelta(hours=int(h),minutes=int(m),seconds=int(s),milliseconds=int(ms))
    def set_timestamps(self):
        matches = re.findall(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n.*",self.srt_data)
        subititles = []
        for subtitle_data in matches:
            subtitle_data = [item for item in subtitle_data.split("\n") if item]
            start,end,text = subtitle_data[0].split("-->")[0].strip(),subtitle_data[0].split("-->")[1].strip(),"".join(subtitle_data[1:])
            start = self._convert_to_timdelta(start)
            end =self._convert_to_timdelta(end)
            subititles.append({
                "start":start.seconds,
                "end":end.seconds,
                "text":text
            })
        return subititles
    def get_opening_timestamps(self):
        for i in range(len(self.subtitle_list)):
            if i + 1 == len(self.subtitle_list):
                break
            subtitle = self.subtitle_list[i]
            subtitle_next = self.subtitle_list[i + 1]
            if (subtitle_next.get("end") - subtitle.get("end")) > 60:
                return {
                    "start":subtitle.get("end"),
                    "end":subtitle_next.get("start") - 10
                }
    def get_ending_timestamps(self):
        for i in range(len(self.subtitle_list)):
            if i + 1 == len(self.subtitle_list):
                break
            subtitle = self.subtitle_list[i]
            subtitle_next = self.subtitle_list[i + 1]
            if subtitle.get("end") > 500:
                if (subtitle_next.get("end") - subtitle.get("end") > 60):
                    return {
                        "start":subtitle.get("end"),
                        "end":subtitle_next.get("end")
                    }
        return {
            "start":self.subtitle_list[-1].get("end"),
            "end":self.subtitle_list[-1].get("end") + 85
        }





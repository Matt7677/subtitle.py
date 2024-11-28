from datetime import timedelta
import re


class NotSRTError(Exception):
    def __init__(self,msg=None):
        super().__init__(msg="Specified file is not SRT" or msg)



class SRTHandler:
    def __init__(self,srt_file=None):
        self.srt_data = open(srt_file,"r").read()
        self.subtitle_list = sorted(self.set_timestamps(),key=lambda x:x.get("start")) 
    def _convert_to_timdelta(self,time_str):
        time_str = re.sub(r"[:,]"," ",time_str)
        h,m,s,ms = time_str.split(" ")
        return timedelta(hours=int(h),minutes=int(m),seconds=int(s),milliseconds=int(ms))
    def set_timestamps(self):
        srt_data = [item for item in self.srt_data.split("\n\n") if item]
        #matches = re.findall(r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n.*",srt_data)
        if not srt_data:
            raise NotSRTError()
        subititles = []
        for subtitle_data in srt_data:
            subtitle_data = subtitle_data.split("\n")
            for char in subtitle_data:
                if char.isdigit():
                    subtitle_data.remove(char)
                elif char == "\ufeff1":
                    subtitle_data.remove(char)
            start,end,text = subtitle_data[0].split("-->")[0].strip(),subtitle_data[0].split("-->")[1].strip(),"".join(subtitle_data[1:])
            start = self._convert_to_timdelta(start)
            end =self._convert_to_timdelta(end)
            subititles.append({
                "start":start.total_seconds(),
                "end":end.total_seconds(),
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
    def search_sentence(self,text):
        for item in self.subtitle_list:
            if item.get("text") == text:
                return item


class ASSHandler:
    def __init__(self,file):
        self.ass_data = open(file,"r").read()
    def _convert_to_timdelta(self,time_str):
        time_str = re.sub(r"[:.]"," ",time_str)
        h,m,s,ms = time_str.split(" ")
        return timedelta(hours=int(h),minutes=int(m),seconds=int(s),milliseconds=int(ms))
    def set_timestamps(self):
        ass_data = re.findall(r"Dialogue: \d+,\d+:\d+:\d+.\d+,\d+:\d+:\d+.\d+.*",self.ass_data)
        final = []
        for dialogue in ass_data:
            regex = r"\d+:\d+:\d+.\d+"
            results = re.findall(regex,dialogue)
            start,end = results[0],results[1]
            text = re.findall(r"[\u4e00-\u9fff\u3040-\u309f\uff60-\uff9f]",dialogue)
            text = "".join(text)
            start,end = self._convert_to_timdelta(start).total_seconds(),self._convert_to_timdelta(end).total_seconds()
            final.append({
                "start":start,
                "end":end,
                "text":text
            })

        return final



class Subtitle():
    def __new__(cls,file):
        ext = file.split(".")[-1]
        match(ext):
            case "srt":
                return SRTHandler(file)
            case "ass":
                return ASSHandler(file)
            case _:
                raise Exception(f"Unsuported File Type {ext}")
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
    def search_sentence(self,text):
        for item in self.subtitle_list:
            if item.get("text") == text:
                return item

import os
import sys
import json
import inspect

class bib_manager:

    def __init__(self, user_input1="", user_input2="", user_input3=""):
        self.sendout_debug = False
        self.sendout_process = True
        self.sendout_info = True
        self.sendout_warning = True
        if self.sendout_process :
            self.sendout_info = True
        self.init_manager()
        option1 = ""
        if user_input1 in self.run_type_options:
            option1 = user_input1
            user_input1 = ""
        if user_input1:
            if   user_input1.endswith(".ris"):  self.parse_ris(user_input1)
            elif user_input1.endswith(".json"): self.parse_json(user_input1)
            else:                               self.parse_bibtex(user_input1)
        else:
             self.run_manager(option1, user_input2, user_input3)

    def init_manager(self):
        self.clear_fields()
        self.run_type_options = {
            "q":9,
            "0":0, "new":0,
            "1":1, "nav":1, "navigate":1,
        }
        self.collaboration_list = []
        self.journal_list = []
        self.dictionary_of_ris_formats = {}
        self.required_fields = {}
        self.optional_fields = {}
        self.read_list_of_journals()
        self.read_list_of_entry_types()
        self.read_list_of_collaborations()
        self.read_list_of_ris_formats()

    def clear_fields(self):
        self.bib_fields = {}

    def exit_bib_manager(self):
        print_info(f"exit from {inspect.getframeinfo(inspect.stack()[1][0]).function})")
        exit()

    def input_question(self, question):
        user_input = input(f"\033[0;36m=== {question}\033[0m").strip()
        return user_input

    def print_process(self, content, always_sendout=False, make_block=False):
        if make_block:
            line_break = "____________________________________________________________________________________"
            content = f"{line_break}\n{content.strip()}\n{line_break}"
        if self.sendout_process or always_sendout:
            print(f'{content}')

    def print_info   (self, content, always_sendout=False): print(f'\033[0;32m***\033[0m {content}')      if (self.sendout_info    or always_sendout) else 0
    def print_warning(self, content, always_sendout=False): print(f'\033[0;32mwarning!\033[0m {content}') if (self.sendout_warning or always_sendout) else 0
    def print_error  (self, content, always_sendout=False): print(f'\033[0;32merror!\033[0m {content}')   if (self.sendout_error   or always_sendout) else 0
    def print_list   (self, tt, val, always_sendout=False): print(f'\033[0;34m{tt}\033[0m {val}')         if (self.sendout_info    or always_sendout) else 0

    def print_debug(self, content, always_sendout=False):
        callerframerecord = inspect.stack()[1]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        if self.sendout_debug or always_sendout:
            print(f"\033[0;36m+{info.lineno} {info.filename} \033[0;36m# ({info.function})\033[0m {content}")

    def print_always(self, content, always_sendout=False):
        callerframerecord = inspect.stack()[1]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        print(f"\033[0;36m+{info.lineno} {info.filename} \033[0;36m# ({info.function})\033[0m {content}")



    def print_all_fields(self):
        self.print_info(f'Printing fields of {self.bib_fields["bname"]}  ({self.bib_fields["xname"]})')
        list_of_keys = []
        for key_name in self.bib_fields:
            self.print_field(key_name,len(list_of_keys))
            list_of_keys.append(key_name)

    def print_field(self, key, idx=-1):
        if idx>=0: self.print_list(f"{str(idx)+')':>3}", f"{key:20}{self.bib_fields[key]}")
        else:      self.print_list(f"{'>':>3}",  f"{key:20}{self.bib_fields[key]}")

    def read_list_of_entry_types(self):
        f1 = open('data/common/list_of_entry_types','r')
        new_type = True
        following_is_required_fields = False
        following_is_optional_fields = False
        type_name = ""
        type_equal_to = ""
        line_required = ""
        line_optional = ""
        while True:
            line = f1.readline()
            if not line: break
            line = line.strip()
            if len(line)==0:
                new_type = True
                if len(type_name)>0:
                    line_required = line_required.strip()
                    line_optional = line_optional.strip()
                    self.required_fields[type_name] = []
                    self.optional_fields[type_name] = []
                    if len(type_equal_to)>0:
                         self.required_fields[type_name] = self.required_fields[type_equal_to] 
                         self.optional_fields[type_name] = self.optional_fields[type_equal_to] 
                    else:
                        for field in line_required.split(","):
                            if field.find("/")>=0: field = field[:field.find("/")]
                            field = field.lower().strip()
                            self.required_fields[type_name].append(field)
                        for field in line_optional.split(","):
                            if field.find("/")>=0: field = field[:field.find("/")]
                            field = field.lower().strip()
                            self.optional_fields[type_name].append(field)
                type_name = ""
                type_equal_to = ""
                line_required = ""
                line_optional = ""
                following_is_required_fields = False
                following_is_optional_fields = False
                continue
            elif new_type:
                type_name = line
                new_type = False
                continue
            elif line[0]=='*':
                type_equal_to = line[1:]
                continue
            elif line[:16]=="Required fields:":
                following_is_required_fields = True
                following_is_optional_fields = False
                line = line[16:]
            elif line[:16]=="Optional fields:":
                following_is_optional_fields = True
                following_is_required_fields = False
                line = line[16:]
            if following_is_required_fields: line_required = line_required + line
            if following_is_optional_fields: line_optional = line_optional + line

    def read_list_of_collaborations(self):
        with open('data/common/list_of_collaborations','r') as f1:
            lines = f1.readlines()
            for line in lines:
                line = line.strip()
                full_name, minimum_name, short_name = line.split('/')
                full_name, minimum_name, short_name = full_name.strip(), minimum_name.strip(), short_name.strip()
                self.print_debug(f"{full_name} / {minimum_name} / {short_name}")
                if len(full_name)>0:
                    self.collaboration_list.append([full_name, minimum_name, short_name])

    def read_list_of_ris_formats(self):
        with open('data/common/list_of_ris_formats','r') as f1:
            lines = f1.readlines()
            for line in lines:
                line = line.strip()
                title_in_ris, title_in_bibtex = line.split()
                self.print_debug(f"{title_in_ris} {title_in_bibtex}")
                self.dictionary_of_ris_formats[title_in_ris] = title_in_bibtex

    def read_list_of_journals(self):
        with open('data/common/list_of_journals','r') as f1:
            lines = f1.readlines()
            for line in lines:
                line = line.strip()
                full_name, minimum_name, short_name = line.split('/')
                full_name, minimum_name, short_name = full_name.strip(), minimum_name.strip(), short_name.strip()
                self.print_debug(f"{full_name} / {minimum_name} / {short_name}")
                if len(full_name)>0:
                    self.journal_list.append([full_name, minimum_name, short_name])

    def run_manager(self, option1="", option2="", option3=""):
        self.print_info("Usage of Bibliography Manager")
        self.print_process("""python3 bib_manager.py bibtex_file.bib  # to write database for bibtex file "bibtex_file.bib" : 
python3 bib_manager.py 0                # to write database from raw
python3 bib_manager.py 1                # to navigate database""")
        self.print_list(f"{'0)':>3}","Navigate")
        self.print_list(f"{'1)':>3}","Write database from raw")
        self.print_list(f"{'q)':>3}","Quite")
        question = "Enter option from above: "
        if not option1:
            option1 = self.input_question(question)
        if not option1:
            self.navigate_database()
        if option1 in self.run_type_options:
            if self.run_type_options[option1]==9: self.exit_bib_manager()
            if self.run_type_options[option1]==0: self.navigate_database(option2,option3)
            if self.run_type_options[option1]==1: self.write_database_from_raw()

    def write_database_from_raw(self):
        pass

    def navigate_database(self, nav_option1="", nav_option2=""):
        #navigate_options = ["bname", "bnumber", "btype", "btag", "collaboration"]
        #for idx, option in enumerate(navigate_options):
        #    self.print_list(f"{f'{idx})':>3}",option)
        #question = "Enter option from above: "
        #user_input = self.input_question(question)
        pass

    def parse_json(self, user_input):
        self.clear_fields()
        with open(user_input,'r') as file_json:
            self.bib_fields = json.load(file_json)
        #self.print_all_fields()
        self.confirm_entry()

    def parse_ris(self, input_file_name):
        f1 = open(input_file_name,'r')
        while True:
            line = f1.readline()
            if not line: break
            line = line.strip()
            if line.find("-")<0:
                self.print_error(f'cannot find "-"!')
                self.print_error(f'This might not be a ris file...')
                self.exit_bib_manager()
            field_title = line.split('-')[0].strip()
            field_value = line.split('-')[1].strip()
            if field_title=="ER":
                self.print_info(f'End of {input_file_name}')
                self.finalize_entry()
                self.confirm_entry()
                self.write_entry()
            else:
                if field_title=="TY":
                    self.clear_fields()
                    self.make_field("btype","article")
                self.make_ris_field(field_title,field_value)

    def parse_bibtex(self, input_file_name):
        f1 = open(input_file_name,'r')
        lines = f1.read()
        while True:
            if len(lines)==0:
                self.print_warning(f'content is empty!')
                break
            self.print_process(lines, make_block=True)
            self.clear_fields()
            iaa = lines.find("@")
            if iaa<0:
                self.print_warning(f'cannot find @!')
                self.print_warning(f'check if the file is in .ris format')
                self.parse_ris(input_file_name)
                self.exit_bib_manager()
            ibr1 = lines.find("{")
            icomma = lines.find(",")
            self.make_field("btype",lines[iaa+1:ibr1])
            self.make_field("xname",lines[ibr1+1:icomma])
            found_aa = False
            lines = lines[icomma+1:]
            while True:
                lines, field_title, field_value = self.find_next_bibtex_entry(lines)
                field_title = field_title.lower()
                if field_title=="": break
                if field_title=='"': continue
                if field_title=="@":
                    found_aa = True
                    break
                self.print_debug(f"{field_title:15} > {field_value}")
                if self.sendout_debug:
                    line_example = lines
                    if len(line_example)>19:
                        line_example = lines[:20].strip() + " ..."
                    self.print_process(f"    -->   {line_example}")
                self.make_field(field_title, field_value)
            self.print_info(f'End of {input_file_name}')
            self.finalize_entry()
            self.confirm_entry()
            self.write_entry()
            if found_aa==False:
                self.print_debug(lines)
                break

    def write_entry(self):
        if "bname" in self.bib_fields:
            file_name_json = f'data/json/{self.bib_fields["bname"]}.json'
            with open(file_name_json,'w') as file_json:
                self.print_info(f'Writting {file_name_json}')
                #https://docs.python.org/ko/3/library/json.html
                #json.dump(obj, fp, *, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True,
                #          cls=None, indent=None, separators=None, default=None, sort_keys=False, **kw)
                json.dump(self.bib_fields,file_json)
                file_json.close()
        if "numbering" in self.bib_fields:
            max_number = -1
            files_in_directory = os.listdir("data/numbering")
            for file_name in files_in_directory:
                try:
                    file_number = int(file_name.split('_')[0])
                    if file_number>max_number:
                        max_number = file_number
                except (ValueError, IndexError):
                    pass
            next_number = max_number + 1
            file_name_numbering = f'data/numbering/{next_number}_{self.bib_fields["bname"]}'
            with open(file_name_numbering,'w') as file_numbering:
                self.print_info(f'Creating {file_name_numbering}')
                pass
        if "collaboration" in self.bib_fields:
            directory_path = f'data/collaboration'
            if self.bib_fields["collaboration"]:
                directory_path = directory_path + f'/{self.bib_fields["collaboration"][1]}'
                os.makedirs(directory_path, exist_ok=True)
                file_name_collaboration = f'{directory_path}/{self.bib_fields["bname"]}'
                with open(file_name_collaboration,'w') as file_collaboration:
                    self.print_info(f'Creating {file_name_collaboration}')
                    pass
        if "btag" in self.bib_fields:
            for tag1 in self.bib_fields["btag"]:
                if not tag1: continue
                directory_path = f'data/tag/{tag1}'
                os.makedirs(directory_path, exist_ok=True)
                file_name_tag1 = f'{directory_path}/{self.bib_fields["bname"]}'
                with open(file_name_tag1,'w') as file_tag1:
                    self.print_info(f'Creating {file_name_tag1}')
                    pass
        if "author" in self.bib_fields:
            author1 = self.bib_fields["author"][0]
            if author1:
                author_nsname = self.make_nospace_author_name(author1)
                directory_path = f'data/author/{author_nsname}'
                os.makedirs(directory_path, exist_ok=True)
                file_name_author = f'{directory_path}/{self.bib_fields["bname"]}'
                with open(file_name_author,'w') as file_author:
                    self.print_info(f'Creating {file_name_author}')
                    pass
        #if "journal" in self.bib_fields:
        #    journal1 = self.bib_fields["journal"][1]
        #    if journal1:
        #        directory_path = f'data/author/{journal1}'
        #        os.makedirs(directory_path, exist_ok=True)
        #        file_name_journal = f'{directory_path}/{self.bib_fields["bname"]}'
        #        with open(file_name_journal,'w') as file_journal:
        #            self.print_info(f'Creating {file_name_journal}')
        #            pass
        #if "bnumber" in self.bib_fields:
        #    bibnumber1 = self.bib_fields["bnumber"]
        #    if journal1:
        #        directory_path = f'data/author/{journal1}'
        #        os.makedirs(directory_path, exist_ok=True)
        #        file_name_journal = f'{directory_path}/{self.bib_fields["bname"]}'
        #        with open(file_name_journal,'w') as file_journal:
        #            self.print_info(f'Creating {file_name_journal}')
        #            pass

    def confirm_entry(self):
        self.print_info("Confirm Entry")
        self.make_bib_name()
        self.print_all_fields()
        question = f"Enter field index to modify the content [index / enter:confirm(continue) / q:quit]: "
        while True:
            user_input = self.input_question(question)
            if user_input=="q":
                self.exit_bib_manager()
            if user_input:
                if user_input.isdigit() and int(user_input)>=0 and int(user_input)<len(self.bib_fields):
                    key_name = list(self.bib_fields.keys())[int(user_input)]
                    self.print_field(key_name)
                    question2 = f"Type value for {key_name}: "
                    user_value = self.input_question(question2)
                    if user_value:
                        self.make_field(key_name,user_value)
                        self.print_field(key_name)
                    else:
                        break
                else:
                    self.print_warning("out of index!")
                    #break
            else:
                break
        self.make_bib_name()

    def finalize_entry(self):
        self.print_info(f"Finalize entry")
        bib_is_arxiv = False
        if self.bib_fields["btype"]=="inproceedings":
            if "archiveprefix" in self.bib_fields:
                bib_is_arxiv = True
        #__TECHINAL_REPORT_______________________________
        if self.bib_fields["btype"]=="techreport":
            if "reportnumber" in self.bib_fields:
                self.bib_fields["volume"] = self.bib_fields["reportnumber"].replace("-","")
            else:
                self.bib_fields["volume"] = ""
            if "institution" in self.bib_fields:
                institution = self.bib_fields["institution"].replace("-","")
                self.make_journal(institution,True)
            else:
                self.make_journal("Techical Report")
            self.bib_fields["page1"] = ""
        #__MISC__________________________________________
        elif self.bib_fields["btype"]=="misc" or bib_is_arxiv:
            key_contain_arxiv = ("archiveprefix" in self.bib_fields)
            url_contain_arxiv = False
            if "url" in self.bib_fields:
                url_contain_arxiv = (self.bib_fields["url"].find("arxiv.org")>=0)
        #__ARXIV_________________________________________
            if key_contain_arxiv or url_contain_arxiv:
                self.make_journal("Arxiv")
                eprint = self.bib_fields["eprint"]
                if eprint.find("/")>=0:
                    self.bib_fields["volume"] = eprint.split("/")[0]
                    self.bib_fields["page1"] = eprint.split("/")[1]
                elif eprint.find("_")>=0:
                    self.bib_fields["volume"] = eprint.split("_")[0]
                    self.bib_fields["page1"] = eprint.split("_")[1]
                elif eprint.find(".")>=0:
                    self.bib_fields["volume"] = eprint.split(".")[0]
                    self.bib_fields["page1"] = eprint.split(".")[1]
                self.bib_fields["volume"] = self.bib_fields["volume"].replace("-","")
        #__NOT_ARXIV_____________________________________
            else:
                self.make_journal("",True)
                self.bib_fields["volume"] = ""
                self.bib_fields["page1"] = ""
        #__THESIS________________________________________
        elif self.bib_fields["btype"]=="phdthesis":
            self.make_journal("PhDThesis",True)
            self.bib_fields["volume"] = ""
            self.bib_fields["page1"] = ""
        #__URL<DOI_______________________________________
        if "doi" in self.bib_fields and "url" not in self.bib_fields:
            url = self.bib_fields["doi"]
            if url.find("https://doi.org/")<0:
               url = "https://doi.org/" + url
            self.make_field("url",url)

    def find_next_bibtex_entry(self, lines):
        field_title = ""
        field_value = ""
        iaa = lines.find("@")
        ieq = lines.find("=")
        ibr1 = lines.find("{")
        if iaa>=0 and ieq>=0 and ibr1>=0 and iaa<ibr1 and iaa<ieq:
            return lines, "@", "@"
        field_title = lines[:ieq].strip()
        lines = lines[ieq+1:]
        inside_bracket = 0
        inside_dbquote = False
        found_init_notation = False
        init_notation_is_bracket = False
        init_notation_is_dbquote = False
        meet_special_command = 1
        signal_end_of_value = False
        count_word_c = 0
        count_all_c = 0
        prev_c = ""
        for curr_c in lines:
            count_all_c = count_all_c + 1
            if curr_c==',' and found_init_notation==False and count_word_c>1:
                signal_end_of_value = True
                self.print_debug(field_title+" "+field_value)
                break
            elif signal_end_of_value:
                if curr_c==',': break
                elif curr_c==' ' or curr_c=="\n": continue
                else:
                    break
                    count_all_c = count_all_c - 1
            elif curr_c=='\\':
                meet_special_command = 0
            elif meet_special_command==0:
                meet_special_command = meet_special_command + 1
            elif curr_c=='{':
                inside_bracket = inside_bracket + 1
                if found_init_notation==False:
                    found_init_notation = True
                    init_notation_is_bracket = True
            elif curr_c=='}':
                inside_bracket = inside_bracket - 1
                if init_notation_is_bracket and inside_bracket==0:
                    signal_end_of_value = True
            elif curr_c=='"':
                if meet_special_command==1 and prev_c=='"':
                    meet_special_command + 1
                else:
                    if found_init_notation==False:
                        found_init_notation = True
                        init_notation_is_dbquote = True
                    if inside_dbquote:
                        inside_dbquote = False
                    else:
                        inside_dbquote = True
                    if init_notation_is_dbquote and inside_dbquote==False:
                        signal_end_of_value = True
            else:
                count_word_c = count_word_c + 1
            prev_c = curr_c
            field_value = field_value + curr_c
        lines = lines[count_all_c:]
        if signal_end_of_value==False:
            return lines, "", ""
        field_value = field_value.strip()
        if len(field_value)>0:
            if field_value[0]=='{':  field_value = field_value[1:].strip()
            if field_value[0]=='"':  field_value = field_value[1:].strip()
            if field_value[-1]=='}': field_value = field_value[:-1].strip()
            if field_value[-1]=='"': field_value = field_value[:-1].strip()
            if field_value[-1]==',': field_value = field_value[:-1].strip()
        return lines, field_title, field_value

    def make_bib_name(self):
        self.print_debug(self.bib_fields["author"])
        name = self.make_nospace_author_name(self.bib_fields["author"][0])
        colb = self.bib_fields["collaboration"][1]
        jour = self.bib_fields["journal"][1]
        year = self.bib_fields["year"]
        volm = self.bib_fields["volume"]
        page = self.bib_fields["page1"]
        btag = self.bib_fields["btag"][0]
        if len(name)>0: name = name + "_"
        if len(colb)>0: colb = colb + "_"
        if len(jour)>0: jour = jour + "_"
        if len(year)>0: year = year + "_"
        if len(volm)>0: volm = volm + "_"
        if len(page)>0: page = page + "_"
        if len(btag)>0: btag = btag + "_"
        bib_name_new = name + colb + jour + year + volm + page + btag
        bib_name_new = bib_name_new[:-1].strip()
        self.bib_fields["bname"] = bib_name_new
        return bib_name_new

    def replace_special_charactors(self, name):
        name = name.strip()
        name = name.replace("\\ifmmode \\acute{n}\else \\'{n}","n")
        name = name.replace("\\acute{n}\\fi{}","n")
        name = name.replace("\\'{n}","n")
        name = name.replace("\\L{}","L")
        name = name.replace("\\l{}","l")
        name = name.replace("\\'{\i}","i")
        name = name.replace("\\i","i")
        name = name.replace('\\""',"")
        name = name.replace("\\''","")
        name = name.replace('\\"',"")
        name = name.replace("\\'","")
        name = name.replace("\\`","")
        name = name.replace("\\^","")
        name = name.replace("\\~","")
        name = name.replace("-","")
        name = name.replace(".","")
        name = name.replace(" ","")
        return name

    def make_nospace_author_name(self, author):
        first_name = self.replace_special_charactors(author[0]).title()
        last_name = self.replace_special_charactors(author[-1]).title()
        middle_name = ""
        if len(author)==3:
            middle_name = self.replace_special_charactors(author[1]).title()
        elif len(author)>3:
            for author0 in author[1:-1]:
                middle_name = middle_name + self.replace_special_charactors(author0).title()
        full_name = last_name + first_name + middle_name
        return full_name

    def make_school(self, field_value):
        self.bib_fields["school"] = field_value
        self.bib_fields["journal"] = self.make_journal(field_value,True)
        self.bib_fields["institute"] = field_value

    def make_doi(self, field_value):
        if field_value.find("https://doi.org/")>=0:
           field_value =  field_value.replage("https://doi.org/","")
        self.bib_fields["doi"] = field_value

    def make_month(self, field_value):
        field_value.lower()
        if field_value=="1"  or field_value.find("jan")==0 : field_value = "Jan"
        if field_value=="2"  or field_value.find("feb")==0 : field_value = "Feb"
        if field_value=="3"  or field_value.find("mar")==0 : field_value = "Mar"
        if field_value=="4"  or field_value.find("apr")==0 : field_value = "Apr"
        if field_value=="5"  or field_value.find("may")==0 : field_value = "May"
        if field_value=="6"  or field_value.find("jun")==0 : field_value = "Jun"
        if field_value=="7"  or field_value.find("jul")==0 : field_value = "Jul"
        if field_value=="8"  or field_value.find("aug")==0 : field_value = "Aug"
        if field_value=="9"  or field_value.find("sep")==0 : field_value = "Sep"
        if field_value=="10" or field_value.find("oct")==0 : field_value = "Oct"
        if field_value=="11" or field_value.find("nov")==0 : field_value = "Nov"
        if field_value=="12" or field_value.find("dec")==0 : field_value = "Dec"
        self.bib_fields["month"].append(field_value)

    def make_btag(self, field_value):
        for tag1 in field_value.split(','):
            tag1 = tag1.strip()
            if not tag1:
                continue
            if self.bib_fields["btag"][0]=='':
                self.bib_fields["btag"][0] = tag1
            else:
                self.bib_fields["btag"].append(tag1)

    def make_archivePrefix(self, field_value):
        self.make_journal("Arxiv")

    def make_journal(self, field_value, register_temporarily=False):
        if register_temporarily:
            journal1 = field_value.strip()
            journal2 = self.replace_special_charactors(field_value.strip())
            journal3 = field_value.strip()
            if journal2.find(" ")>=0:
                split_journal2 = journal2.split()
                journal2 = ""
                for token_journal2 in split_journal2:
                    journal2 = journal2 + token_journal2[0].upper()
            self.print_warning(f'The journal "{field_value}" from {self.bib_fields["xname"]} will be added temporarily: {journal1} / {journal2} / {journal3}')
            self.bib_fields["journal"] = [journal1,journal2,journal3]
        elif len(field_value)>0:
            found_etnry = False
            for journal_entry in self.journal_list:
                if journal_entry[0]==field_value:
                    self.bib_fields["journal"] = journal_entry
                    found_etnry = True
                    break
            if found_etnry==False:
                self.print_error(f'Add journal "{field_value}" to journal list!')
                self.exit_bib_manager()
        else:
            self.print_warning(f'Journal is empty!')
            self.bib_fields["journal"] = ["","",""]

    def make_collaboration(self, field_value, register_temporarily=False):
        #if register_temporarily:
        #    collaboration1 = field_value.strip()
        #    collaboration2 = field_value.strip()
        #    collaboration3 = field_value.strip()
        #    if collaboration2.find(" ")>=0:
        #        split_collaboration2 = collaboration2.split()
        #        collaboration2 = ""
        #        for token_collaboration2 in split_collaboration2:
        #            collaboration2 = collaboration2 + token_collaboration2[0].upper()
        #    print_info('The collaboration "{field_value}" from {self.bib_fields["xname"]} will be added temporarily: {collaboration1} / {collaboration2} / {collaboration3}')
        #    self.bib_fields["collaboration"] = [collaboration1,collaboration2,collaboration3]
        #elif len(field_value)>0:
        if len(field_value)>0:
            found_etnry = False
            for collaboration_entry in self.collaboration_list:
                if collaboration_entry[0]==field_value:
                    self.bib_fields["collaboration"] = collaboration_entry
                    found_etnry = True
                    break
            if found_etnry==False:
                self.print_error('Add collaboration "{field_value}" to collaboration list!')
                self.exit_bib_manager()
        self.print_debug(f'collaboration : {self.bib_fields["collaboration"][0]}  /  {self.bib_fields["collaboration"][1]}  /  {self.bib_fields["collaboration"][2]}')

    def make_pages(self, field_value):
        self.bib_fields["pages"] = field_value
        self.bib_fields["page1"] = ""
        self.bib_fields["page2"] = ""
        if field_value.find("--")>=0:
            self.bib_fields["page1"] = field_value.split("--")[0]
            self.bib_fields["page2"] = field_value.split("--")[1]
        elif field_value.find("-")>=0:
            self.bib_fields["page1"] = field_value.split("-")[0]
            self.bib_fields["page2"] = field_value.split("-")[1]
        else:
            self.bib_fields["page1"] = field_value
            self.bib_fields["page2"] = 0
        self.print_debug(f'pages : {self.bib_fields["page1"]} - {self.bib_fields["page2"]}')

    def make_btype(self, field_value):
        type_name = field_value.lower()
        self.bib_fields["bname"] = ""
        self.bib_fields["bnumber"] = -1
        self.bib_fields["btype"] = type_name
        self.bib_fields["btag"] = [""]
        self.bib_fields["collaboration"] = ["","",""]
        #self.bib_fields["physics"] = []
        #self.bib_fields["reaction"] = [[]]
        #self.bib_fields["beam-energy"] = [[]]
        #self.bib_fields["detector"] = [[]]
        #self.bib_fields["experiment"] = []
        #self.bib_fields["theory"] = []
        #self.bib_fields["observation"] = []
        #self.bib_fields["observable"] = []
        #self.bib_fields["tool"] = []
        self.bib_fields["xname"] = ""
        if type_name in self.required_fields:
            for field in self.required_fields[type_name]:
                self.bib_fields[field] = ""
        else:
            self.print_warning(f'Add type "{type_name}" to type list!')

    def configure_ris_field_title(self, field_title):
        if field_title not in self.dictionary_of_ris_formats:
            self.print_warning(f'The type "{field_title}" do not exist in ris format list!')
            self.exit_bib_manager()
        return self.dictionary_of_ris_formats[field_title]

    def configure_ris_field_value(self, field_title, field_value):
        #if field_title=="TY" and field_value=="JOUR":
        #    return "article"
        return field_value

    def make_ris_field(self, field_title, field_value):
        field_value = self.configure_ris_field_value(field_title, field_value)
        field_title = self.configure_ris_field_title(field_title)
        self.print_debug(f"{field_title:15} > {field_value}")
        self.make_field(field_title, field_value)
        
    def make_field(self, field_title, field_value):
        if   field_title=="doi"           : self.make_doi(field_value)
        elif field_title=="btag"          : self.make_btag(field_value)
        elif field_title=="month"         : self.make_month(field_value)
        elif field_title=="btype"         : self.make_btype(field_value)
        elif field_title=="pages"         : self.make_pages(field_value)
        elif field_title=="author"        : self.make_author(field_value)
        elif field_title=="school"        : self.make_school(field_value)
        elif field_title=="journal"       : self.make_journal(field_value)
        elif field_title=="collaboration" : self.make_collaboration(field_value)
        else:
            self.bib_fields[field_title] = field_value

    def make_author(self, field_value):
        name_is_last_to_first = False
        author_names = field_value.split(" and ")
        author_list = []
        for author_name in author_names:
            names = self.parse_author_name(author_name)
            author_list.append(names)
        self.bib_fields["author"] = author_list

    def parse_author_name(self, author_name):
        author_name = author_name.strip()
        last_name = ""
        first_name = ""
        if author_name[0]=="{" and author_name[-1]=="}":
            first_name = author_name[1:-1]
        elif author_name.find(",")>=0:
            author_name_break = author_name.split(",")
            num_breaks = len(author_name_break)
            last_name = author_name_break[0].strip()
            first_name = author_name_break[1].strip()
        else:
            ispace = author_name.rfind(" ")
            first_name = author_name[:ispace].strip()
            last_name = author_name[ispace:].strip()
        ispace = first_name.find(" ")
        names = []
        name_list = first_name.split()
        self.print_debug(f"name_list: {name_list}")
        for name in name_list:
            idot = name.find(".")
            while idot>0 and idot<len(name)-1:
                name2 = name[:idot+1].strip()
                name  = name[idot+1:].strip()
                if name2:
                    names.append(name2)
                idot = name.find(".")
            else:
                 names.append(name)
        names.append(last_name)
        self.print_debug(names)
        return names



if __name__ == "__main__":
    if len(sys.argv)==2: bib_manager(sys.argv[1])
    elif len(sys.argv)==3: bib_manager(sys.argv[1],sys.argv[2])
    elif len(sys.argv)==4: bib_manager(sys.argv[1],sys.argv[2],sys.argv[3])
    else:
        bib_manager()



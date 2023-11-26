#!/usr/bin/env python3

import os
import sys
import json
import inspect

class bib_manager:

    def __init__(self, user_input1="", user_input2="", user_input3=""):
        #self.print_debug(f"{user_input1} {user_input2} {user_input3}")
        self.sendout_debug = False
        self.sendout_process = True
        self.sendout_info = True
        self.sendout_warning = True
        self.sendout_error = True
        if self.sendout_process : self.sendout_info = True
        self.init_manager()
        run_option_numbers = ([run_option[0] for run_option in self.run_options])
        run_option_explain = ([run_option[1] for run_option in self.run_options])
        run_option_function = ([run_option[2] for run_option in self.run_options])
        if user_input1 and user_input1 not in run_option_numbers:
            if user_input1.find('.')>0:
                self.parse_input(user_input1)
            else:
                self.navigate_title(user_input1)
        elif user_input1 and user_input1 in run_option_numbers:
            run_option_index = run_option_numbers.index(user_input1)
            self.print_always(self.run_options[run_option_index][2])
            self.run_options[run_option_index][2]()
        else:
            self.print_info("Usage of Bibliography Manager")
            for idx in range(len(run_option_numbers)):
                self.print_title(f"python3 bib_manager.py {run_option_numbers[idx]:20} # {run_option_explain[idx]}")
            user_input_idx, user_input_value = self.enumerate_and_select_from_list(run_option_explain)
            if user_input_value:
                self.run_options[user_input_idx][2]()

    def init_manager(self):
        self.clear_fields()
        self.run_options = [
            ["0", 'navigate database',         self.navigate_database,       "nav", "navigate"],
            ["1", 'write database from raw',   self.write_database_from_raw, "new"],
            ["2", 'write database from input', self.parse_input,             "input"],
            ["9", 'quite',                     self.exit_bib_manager,        "quit"]
        ]
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
        self.print_info(f"exit from ({inspect.getframeinfo(inspect.stack()[1][0]).function})")
        exit()

    def input_question(self, question):
        user_input = input(f"\033[0;36m=== {question}\033[0m").strip()
        return user_input

    def input_options(self, options, question="Type option number(s) to Add. Type <Enter> if non: "):
        list(options)
        idx_option = {}
        for idx, key in enumerate(list(options)):
            if idx+1<10:
                idxalp = str(idx+1)
            else:
                idxalp = chr((idx-10) + 97)
            self.print_list(f"{idxalp:3>})",key)
            idx_option[idxalp] = key
        user_options = input(question)
        self.print_info("Selected option(s):")
        list_chosen_key = []
        if len(user_options)!=0:
            for idxalp in user_options:
                key = idx_option[idxalp]
                list_chosen_key.append(key)
                self.print_list(f"{idxalp:3>})",key)
        return list_chosen_key

    def print_title(self, content, always_sendout=False, make_block=False):
        if make_block:
            line_break = "____________________________________________________________________________________"
            content = f"{line_break}\n{content.strip()}\n{line_break}"
        if self.sendout_process or always_sendout:
            print(f'{content}')

    def print_info   (self, content, always_sendout=False): print(f'\033[0;32m***\033[0m {content}')      if (self.sendout_info    or always_sendout) else 0
    def print_warning(self, content, always_sendout=False): print(f'\033[0;33mwarning!\033[0m {content}') if (self.sendout_warning or always_sendout) else 0
    def print_error  (self, content, always_sendout=False): print(f'\033[0;31merror!\033[0m {content}')   if (self.sendout_error   or always_sendout) else 0
    def print_list   (self, tt, val, always_sendout=False): print(f'\033[0;34m{tt}\033[0m {val}')         if (self.sendout_info    or always_sendout) else 0

    def print_debug(self, content, always_sendout=False):
        callerframerecord = inspect.stack()[1]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        if self.sendout_debug or always_sendout:
            print(f"\033[0;36m+{info.lineno} {info.filename} \033[0;36m# ({info.function})\033[0m {content}")

    def print_always(self, content="", always_sendout=False):
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
            if len(line)==0: continue
            header, content = line[0], line[1:].strip()
            if header=="#":
                continue
            if header=="*":
                type_name = content
                self.required_fields[type_name] = []
                self.optional_fields[type_name] = []
                #if "bname"         not in self.required_fields: self.optional_fields[type_name].append("bname")
                #if "bnumber"       not in self.required_fields: self.optional_fields[type_name].append("bnumber")
                #if "btype"         not in self.required_fields: self.optional_fields[type_name].append("btype")
                #if "btag"          not in self.required_fields: self.optional_fields[type_name].append("btag")
                if "collaboration" not in self.required_fields: self.optional_fields[type_name].append("collaboration")
                if "reference"     not in self.required_fields: self.optional_fields[type_name].append("reference")
                if "citedby"       not in self.required_fields: self.optional_fields[type_name].append("citedby")
                if "reaction"      not in self.required_fields: self.optional_fields[type_name].append("reaction")
            if header=="1":
                if content not in self.required_fields: self.required_fields[type_name].append(content)
            if header=="9":
                if content not in self.required_fields: self.optional_fields[type_name].append(content)
            if header=="*":
                type_equal_to = content
                self.required_fields[type_name] = self.required_fields[type_equal_to]
                self.optional_fields[type_name] = self.optional_fields[type_equal_to]

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

    def enumerate_and_select_from_list(self, options):
        idxMax = 0
        for idx, option in enumerate(options):
            self.print_list(f"{f'{idx})':>3}",option)
            idxMax = idx
        question = "Enter index/name from above: "
        user_input = self.input_question(question)
        idxSelect = -1
        if user_input in options:
            idxSelect = options.index(user_input)
        if idxSelect<0 and user_input.isdigit() and int(user_input)<=idxMax:
            idxSelect = int(user_input)
        if idxSelect>0:
            keySelect = options[idxSelect]
            return idxSelect, keySelect
        return -1, ""

    def enumerate_and_select_from_dict(self, options):
        idxMax = 0
        for idx, option in enumerate(options):
            self.print_list(f"{f'{idx})':>3}",option)
            idxMax = idx
        question = "Enter index/name from above: "
        user_input = self.input_question(question)
        idxSelect = -1
        if user_input in options:
            idxSelect = list(options.keys()).index(user_input)
        if idxSelect<0 and user_input.isdigit() and int(user_input)<=idxMax:
            idxSelect = int(user_input)
        if idxSelect>0:
            keySelect = list(options.keys())[idxSelect]
            return idxSelect, keySelect
        return -1, ""

    def write_database_from_raw(self):
        self.print_info("Write database from raw")
        key_idx, key_selected = self.enumerate_and_select_from_dict(self.required_fields)
        self.make_field("btype", key_selected)
        self.finalize_entry()
        #self.confirm_entry()
        #self.write_entry()
        #if key_selected:
        #    self.print_info(key_selected)
        #    required_fields = self.required_fields[key_selected]
        #    required_fields = self.optional_fields[key_selected]
        #    self.print_info(required_fields)
        #    for field in required_fields:
        #        user_input = ""
        #        while len(user_input)==0:
        #            user_input = self.input_question(f"Enter content for {field}: ")
        #            if user_input=="x":
        #                self.exit_bib_manager()
        #        self.make_field("btype","article")
        #    #self.print_info(self.required_fields[key_selected])
        #    #self.print_info(self.optional_fields[key_selected])
        #pass

    def add_reference(self):
        self.print_always()
        pass

    def add_citedby(self):
        self.print_always()
        pass

    def navigate_database(self, nav_option1="", nav_option2=""):
        self.print_info("Navigate database")
        self.print_always()
        navigate_options = ["name", "number", "type", "tag", "collaboration"]
        navigate_options = {
            "name":0,
            "number":1,
            "type":2,
            "tag":3,
            "collaboration":4
        }
        #input_option = self.input_options(navigate_options)[0]
        #print(input_option)
        #self.navigate_author()
            #data/author
        #for idx, option in enumerate(navigate_options):
        #    self.print_list(f"{f'{idx})':>3}",option)
        #question = "Enter option from above: "
        #user_input = self.input_question(question)
        #if user_input=="name":
        #    pass

    def navigate_author(self):
        list_of_files = os.listdir("data/author")
        print(list_of_files)

    def navigate_title(self,user_input):
        list_of_files = os.listdir("data/json")
        for file_name in list_of_files:
            if file_name.find(user_input)>=0:
                self.parse_json(f"data/json/{file_name}")
                return
        self.print_warning(f"No matching {user_input}")

    def parse_input(self,user_input1=""):
        if not user_input1:
            list_of_files = os.listdir("./")
            user_input_array = self.input_options(list_of_files)
            if len(user_input_array)==0:
                self.exit_bib_manager()
            user_input1 = user_input_array[0]
        if   user_input1.endswith(".ris"):  self.parse_ris(user_input1)
        elif user_input1.endswith(".json"): self.parse_json(user_input1)
        else:                               self.parse_bibtex(user_input1)

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
            #field_title = line.split('-')[0].strip()
            #field_value = line.split('-')[1].strip()
            field_title = line[:line.find('-')].strip()
            field_value = line[line.find('-')+1:].strip()
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
            self.print_title(lines, make_block=True)
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
                    self.print_title(f"    -->   {line_example}")
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
            if self.bib_fields["collaboration"][0]:
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
                author_nsname = self.make_author_name_flat(author1)
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
                        continue
                else:
                    self.print_warning("out of index!")
                    #break
            else:
                break
        self.make_bib_name()
        self.make_bib_cite()
        self.print_all_fields()

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
        name = self.make_author_name_flat(self.bib_fields["author"][0])
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

    def make_bib_cite(self):
        self.print_debug(self.bib_fields["author"])
        name = self.make_author_name_cite(self.bib_fields["author"][0])
        jour = self.bib_fields["journal"][2]
        volm = self.bib_fields["volume"]
        year = self.bib_fields["year"]
        page = self.bib_fields["page1"]
        if len(name)>0:
            if len(self.bib_fields["author"])>1:
                name = name + " et. al., "
            else:
                name = name + ", "
        if len(jour)>0: jour = jour + " "
        if len(volm)>0: volm = volm + " "
        if len(year)>0: year = f"({year}) "
        if len(page)>0: page = page
        bib_cite_new = name + jour + volm + year + page
        bib_cite_new = bib_cite_new.strip()
        self.bib_fields["bcite"] = bib_cite_new
        return bib_cite_new

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

    def make_author_name_flat(self, author):
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

    def make_author_name_cite(self, author):
        first_name = (author[0]).title()
        last_name = (author[-1]).title()
        full_name = f"{first_name.title()} {last_name.title()}"
        return full_name

    def make_school(self, field_value):
        self.bib_fields["school"] = field_value
        self.bib_fields["journal"] = self.make_journal(field_value,True)
        self.bib_fields["institute"] = field_value

    def make_doi(self, field_value):
        if field_value.find("https://doi.org/")>=0:
           field_value =  field_value.replace("https://doi.org/","")
        self.bib_fields["doi"] = field_value

    def make_month(self, field_value):
        field_value = field_value.lower()
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
        self.bib_fields["month"] = field_value

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
                self.print_error(f'Add journal "{field_value}" to journal list data/common/list_of_journals !')
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
        self.bib_fields["author"] = []
        self.bib_fields["collaboration"] = ["","",""]
        self.bib_fields["reference"] = {}
        self.bib_fields["citedby"] = {}
        self.bib_fields["reaction"] = []
        #self.bib_fields["physics"] = []
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
                if field not in self.bib_fields:
                    self.bib_fields[field] = ""
        else:
            self.print_warning(f'Add type "{type_name}" to type list!')

    def make_reaction(self, field_value):
        reaction_array = field_value.split()
        self.bib_fields["reaction"].append(reaction_array)
        reaction_string = '_'.join(reaction_array)
        self.make_btag(reaction_string)

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
        elif field_title=="reaction"      : self.make_reaction(field_value)
        elif field_title=="pages"         : self.make_pages(field_value)
        elif field_title=="author"        : self.make_author(field_value)
        elif field_title=="school"        : self.make_school(field_value)
        elif field_title=="journal"       : self.make_journal(field_value)
        elif field_title=="collaboration" : self.make_collaboration(field_value)
        else:
            self.bib_fields[field_title] = field_value

    def make_author(self, field_value):
        name_is_last_to_first = False
        if field_value.count(",")>1 and field_value.count("and")==1:
            field_value = field_value.replace(" and ",", ")
            author_names = field_value.split(",")
        else:
            author_names = field_value.split(" and ")
        author_list = self.bib_fields["author"]
        for author_name in author_names:
            names = self.parse_author_name(author_name)
            author_list.append(names)
        #self.print_always(names)
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
                    if name2.find("{")==0 and name2.find("}")==len(name2)-1:
                        name2 = name2[1:-1]
                    names.append(name2)
                idot = name.find(".")
            else:
                if name.find("{")==0 and name.find("}")==len(name)-1:
                    name = name[1:-1]
                names.append(name)
        if last_name.find("{")==0 and last_name.find("}")==len(last_name)-1:
            last_name = last_name[1:-1]
        names.append(last_name)
        self.print_debug(names)
        return names


if __name__ == "__main__":
    if   len(sys.argv)==2: bib_manager(sys.argv[1])
    elif len(sys.argv)==3: bib_manager(sys.argv[1],sys.argv[2])
    elif len(sys.argv)==4: bib_manager(sys.argv[1],sys.argv[2],sys.argv[3])
    else:
        bib_manager()

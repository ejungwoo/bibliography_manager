import os
import sys
import json
import inspect

class bib_manager:

    def __init__(self, input_file_name=""):
        self.sendout_notice = False
        self.sendout_process = True
        self.sendout_debug = False
        self.sendout_warning = False
        self.sendout_debug = False
        self.init()
        input_number = -1
        if input_file_name.isdigit() and len(input_file_name)==0:
            input_number = int(input_file_name)
            input_file_name = ""
        if input_file_name:
            if input_file_name.endswith(".ris"):
                self.read_ris(input_file_name)
            else:
                self.read_bibtex(input_file_name)
        else:
             self.run_manager(input_number)

    def init(self):
        self.clear_fields()
        self.collaboration_list = []
        self.journal_list = []
        self.required_fields = {}
        self.optional_fields = {}
        self.read_list_of_journals()
        self.read_list_of_entry_types()
        self.read_list_of_collaborations()

    def clear_fields(self):
        self.bib_fields = {}

    def print_warning(self, content, always_sendout=False):
        if self.sendout_warning or always_sendout:
            print(f'//////////   WARNING! {content}   //////////')

    def print_error(self, content, always_sendout=False):
        if self.sendout_error or always_sendout:
            print(f'!!!!!!!!!!   ERROR! {content}   !!!!!!!!!!')

    def print_debug(self, content, always_sendout=False):
        callerframerecord = inspect.stack()[1]
        frame = callerframerecord[0]
        info = inspect.getframeinfo(frame)
        if self.sendout_debug or always_sendout:
            script_name = os.path.basename(__file__)
            #print(f"+{info.lineno} {info.filename} # ({info.function}) {content}")
            print(f"\033[0;36m+{info.lineno} {info.filename} # ({info.function}) {content}\033[0;36m#\033[0m")
            #std::cout<<"+\033[0;36m"<<Form("%d ",line)<<"\033[0m "<<Form("%s \033[0;36m#\033[0m ", title.c_str());

    def print_all_fields(self):
        print()
        print(f'+++ {self.bib_fields["bibname"]}  ({self.bib_fields["oldname"]})')
        list_of_keys = []
        for key_name in self.bib_fields:
            self.print_field(key_name,len(list_of_keys))
            list_of_keys.append(key_name)
        print()

    def print_field(self, key, idx=-1):
        if self.sendout_process:
            if idx>=0:
                print(f"{idx:>2}) {key:20}{self.bib_fields[key]}")
            else:
                print(f"{'':>2}> {key:20}{self.bib_fields[key]}")

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
                            self.required_fields[type_name].append(field.strip())
                        for field in line_optional.split(","):
                            if field.find("/")>=0: field = field[:field.find("/")]
                            self.optional_fields[type_name].append(field.strip())
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
                if self.sendout_debug: print(f"{full_name} / {minimum_name} / {short_name}")
                if len(full_name)>0:
                    self.collaboration_list.append([full_name, minimum_name, short_name])

    def read_list_of_journals(self):
        with open('data/common/list_of_journals','r') as f1:
            lines = f1.readlines()
            for line in lines:
                line = line.strip()
                full_name, minimum_name, short_name = line.split('/')
                full_name, minimum_name, short_name = full_name.strip(), minimum_name.strip(), short_name.strip()
                if self.sendout_debug: print(f"{full_name} / {minimum_name} / {short_name}")
                if len(full_name)>0:
                    self.journal_list.append([full_name, minimum_name, short_name])

    def read_ris(self, input_file_name):
        pass

    def run_manager(self, input_number=-1):
        print("""
* Usage of Bibliography Manager
python3 bib_manager.py bibtex_file.bib  # to write database for bibtex file "bibtex_file.bib" : 
python3 bib_manager.py 0                # to write database from raw
python3 bib_manager.py 1                # to navigate database""")
        question = f"""
 0) Write database from raw
 1) Navigate
 q) Quite
=== Enter option from above: """
        options = ["0","1","q"]
        user_input = input(question).strip()
        if not user_input:
            self.navigate_database()
        if user_input in options:
            if user_input=="q":
                print("QUIT!")
                exit()
            if user_input=="0": self.write_database_from_raw()
            if user_input=="1": self.navigate_database()

    def write_database_from_raw(self):
        pass

    def navigate_database(self):
        #files_in_directory = os.listdir("data/json/")
        pass

    def read_bibtex(self, input_file_name):
        #if len(input_file_name)==0:
        #    input_file_name = input("enter bibtext content: ")
        f1 = open(input_file_name,'r')
        lines = f1.read()
        while True:
            if len(lines)==0:
                print_warning(f'content is empty!')
                break
            if self.sendout_process:
                print("\n")
                print(f"________________________________________________________________________________")
                print(lines)
                print(f"________________________________________________________________________________")
            self.clear_fields()
            iaa = lines.find("@")
            if iaa<0:
                print_warning(f'cannot find @!')
                break
            ibr1 = lines.find("{")
            icomma = lines.find(",")
            self.make_type(lines[iaa+1:ibr1])
            self.make_field("oldname",lines[ibr1+1:icomma])
            found_aa = False
            lines = lines[icomma+1:]
            while True:
                lines, field_title, field_value = self.find_next_entry(lines)
                field_title = field_title.lower()
                if field_title=="": break
                if field_title=='"': continue
                if field_title=="@":
                    found_aa = True
                    break
                if self.sendout_process:
                    print(f"* field : {field_title:15} > {field_value}")
                if self.sendout_debug:
                    line_example = lines
                    if len(line_example)>19:
                        line_example = lines[:20].strip() + " ..."
                    print(f"    -->   {line_example}")
                self.make_field(field_title, field_value)
            if self.sendout_process: print(f'* end of {input_file_name}')
            self.finalize_entry()
            self.confirm_entry()
            self.write_entry()
            if found_aa==False:
                if self.sendout_debug: print(lines)
                break

    def write_entry(self):
        if self.sendout_process: print(f"* write_entry")
        if "bibname" in self.bib_fields:
            file_name_json = f'data/json/{self.bib_fields["bibname"]}.json'
            with open(file_name_json,'w') as file_json:
                print(f'writting {file_name_json}')
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
            file_name_numbering = f'data/numbering/{next_number}_{self.bib_fields["bibname"]}'
            with open(file_name_numbering,'w') as file_numbering:
                print(f'touch {file_name_numbering}')
                pass
        if "collaboration" in self.bib_fields:
            directory_path = f'data/collaboration'
            if self.bib_fields["collaboration"]:
                directory_path = directory_path + f'/{self.bib_fields["collaboration"][1]}'
                os.makedirs(directory_path, exist_ok=True)
                file_name_collaboration = f'{directory_path}/{self.bib_fields["bibname"]}'
                with open(file_name_collaboration,'w') as file_collaboration:
                    print(f'touch {file_name_collaboration}')
                    pass
        if "bibtag" in self.bib_fields:
            for tag1 in self.bib_fields["bibtag"]:
                if not tag1: continue
                directory_path = f'data/tag/{tag1}'
                os.makedirs(directory_path, exist_ok=True)
                file_name_tag1 = f'{directory_path}/{self.bib_fields["bibname"]}'
                with open(file_name_tag1,'w') as file_tag1:
                    print(f'touch {file_name_tag1}')
                    pass
        if "author" in self.bib_fields:
            author1 = self.bib_fields["author"][0]
            if author1:
                author_nsname = self.make_nospace_author_name(author1)
                directory_path = f'data/author/{author_nsname}'
                os.makedirs(directory_path, exist_ok=True)
                file_name_author = f'{directory_path}/{self.bib_fields["bibname"]}'
                with open(file_name_author,'w') as file_author:
                    print(f'touch {file_name_author}')
                    pass


    def confirm_entry(self):
        if self.sendout_process: print(f"* confirm_entry")
        self.make_bib_name()
        self.print_all_fields()
        question = f"=== Enter field index to modify the content [index / enter:continue / q:quit]: "
        while True:
            user_input = input(question)
            if user_input=="q":
                print("QUIT!")
                exit()
            if user_input:
                if user_input.isdigit() and int(user_input)>=0 and int(user_input)<len(self.bib_fields):
                    key_name = list(self.bib_fields.keys())[int(user_input)]
                    self.print_field(key_name)
                    question2 = f"=== Type value for {key_name}: "
                    user_value = input(question2)
                    if user_value:
                        self.make_field(key_name,user_value)
                        self.print_field(key_name)
                    else:
                        break
                else:
                    print("out of index!")
                    #break
            else:
                break
        self.make_bib_name()

    def finalize_entry(self):
        if self.sendout_process: print(f"* finalize_entry")
        bib_is_arxiv = False
        if self.bib_fields["bibtype"]=="inproceedings":
            if "archiveprefix" in self.bib_fields:
                bib_is_arxiv = True
        #__TECHINAL_REPORT_______________________________
        if self.bib_fields["bibtype"]=="techreport":
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
        elif self.bib_fields["bibtype"]=="misc" or bib_is_arxiv:
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
        #__ARXIV_________________________________________
            else:
                self.make_journal("",True)
                self.bib_fields["volume"] = ""
                self.bib_fields["page1"] = ""
        #__THESIS________________________________________
        elif self.bib_fields["bibtype"]=="phdthesis":
            self.make_journal("PhDThesis",True)
            self.bib_fields["volume"] = ""
            self.bib_fields["page1"] = ""

    def find_next_entry(self, lines):
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
                if self.sendout_debug: print("XXXXXXXXXXXXXXXXXXXX", field_title, field_value)
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
        if self.sendout_debug: print(">>>", self.bib_fields["author"])
        name = self.make_nospace_author_name(self.bib_fields["author"][0])
        colb = self.bib_fields["collaboration"][1]
        jour = self.bib_fields["journal"][1]
        year = self.bib_fields["year"]
        volm = self.bib_fields["volume"]
        page = self.bib_fields["page1"]
        btag = self.bib_fields["bibtag"][0]
        if len(name)>0: name = name + "_"
        if len(colb)>0: colb = colb + "_"
        if len(jour)>0: jour = jour + "_"
        if len(year)>0: year = year + "_"
        if len(volm)>0: volm = volm + "_"
        if len(page)>0: page = page + "_"
        if len(btag)>0: btag = btag + "_"
        bib_name_new = name + colb + jour + year + volm + page + btag
        bib_name_new = bib_name_new[:-1].strip()
        self.bib_fields["bibname"] = bib_name_new
        return bib_name_new

    def replace_special_charactors(self, name):
        #if self.sendout_debug: print(name)
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
        if self.sendout_debug: print("xxxxxxxxxxxxxx", author)
        first_name = self.replace_special_charactors(author[0]).title()
        last_name = self.replace_special_cases(author[-1]).title()
        middle_name = ""
        if len(author)==3:
            middle_name = self.replace_special_cases(author[1]).title()
            if self.sendout_debug: print("xxxxxxxxxxxxxx",  middle_name)
        elif len(author)>3:
            for author0 in author[1:-1]:
                middle_name = middle_name + self.replace_special_cases(author0).title()
        full_name = last_name + first_name + middle_name
        if self.sendout_debug: print("xxxxxxxxxxxxxx", full_name)
        return full_name

    def make_school(self, field_value):
        self.bib_fields["school"] = field_value
        self.bib_fields["journal"] = self.make_journal(field_value,True)
        self.bib_fields["institute"] = field_value

    def make_doi(self, field_value):
        self.bib_fields["doi"] = field_value

    def make_bibtag(self, field_value):
        for tag1 in field_value.split(','):
            tag1 = tag1.strip()
            if not tag1:
                continue
            if self.bib_fields["bibtag"][0]=='':
                self.bib_fields["bibtag"][0] = tag1
            else:
                self.bib_fields["bibtag"].append(tag1)

    def make_archivePrefix(self, field_value):
        self.make_journal("Arxiv")

    def make_journal(self, field_value, register_temporarily=False):
        if register_temporarily:
            journal1 = field_value.strip()
            #journal2 = field_value.strip()
            journal2 = self.replace_special_cases(field_value.strip())
            journal3 = field_value.strip()
            if journal2.find(" ")>=0:
                split_journal2 = journal2.split()
                journal2 = ""
                for token_journal2 in split_journal2:
                    journal2 = journal2 + token_journal2[0].upper()
            if self.sendout_notice: print(f'********** NOTE! The journal "{field_value}" from {self.bib_fields["oldname"]} will be added temporarily: {journal1} / {journal2} / {journal3} **********')
            self.bib_fields["journal"] = [journal1,journal2,journal3]
        elif len(field_value)>0:
            found_etnry = False
            for journal_entry in self.journal_list:
                if journal_entry[0]==field_value:
                    self.bib_fields["journal"] = journal_entry
                    found_etnry = True
                    break
            if found_etnry==False:
                print_error(f'Add journal "{field_value}" to journal list!')
                exit()
        else:
            print_warning(f'Journal is empty!')
            self.bib_fields["journal"] = ["","",""]
        #if self.sendout_process: print(f'* journal : {self.bib_fields["journal"][0]}  /  {self.bib_fields["journal"][1]}  /  {self.bib_fields["journal"][2]}')

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
        #    if self.sendout_notice: print(f'********** NOTE! The collaboration "{field_value}" from {self.bib_fields["oldname"]} will be added temporarily: {collaboration1} / {collaboration2} / {collaboration3} **********')
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
                print(f'********** ERROR! Add collaboration "{field_value}" to collaboration list! **********')
                exit()
        if self.sendout_debug: print(f'********** collaboration : {self.bib_fields["collaboration"][0]}  /  {self.bib_fields["collaboration"][1]}  /  {self.bib_fields["collaboration"][2]}')

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
        if self.sendout_debug: print(f'********** pages : {self.bib_fields["page1"]} - {self.bib_fields["page2"]}')

    def make_type(self, field_value):
        type_name = field_value.lower()
        self.bib_fields["bibname"] = ""
        self.bib_fields["bibnumber"] = -1
        self.bib_fields["bibtype"] = type_name
        self.bib_fields["eots"] = "" # experiment, theory, observation, simulation
        self.bib_fields["ptds"] = "" # physics, technical, detector, software
        self.bib_fields["bibtag"] = [""]
        self.bib_fields["collaboration"] = ["","",""]
        self.bib_fields["oldname"] = ""
        if type_name in self.required_fields:
            for field in self.required_fields[type_name]:
                self.bib_fields[field] = ""
        else:
            print_warning(f'Add type "{type_name}" to type list!')

    def make_field(self, field_title, field_value):
        if   field_title=="author"        : self.make_author_list(field_value)
        elif field_title=="journal"       : self.make_journal(field_value)
        elif field_title=="collaboration" : self.make_collaboration(field_value)
        elif field_title=="school"        : self.make_school(field_value)
        elif field_title=="pages"         : self.make_pages(field_value)
        elif field_title=="doi"           : self.make_doi(field_value)
        elif field_title=="bibtag"        : self.make_bibtag(field_value)
        else:
            self.bib_fields[field_title] = field_value

    def make_author_list(self, field_value):
        name_is_last_to_first = False
        author_names = field_value.split(" and ")
        author_list = []
        self.bib_fields["author"] = author_list
        for author_name in author_names:
            names = self.make_author(author_name)
            author_list.append(names)

    def make_author(self, author_name):
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
        if self.sendout_debug: print(f"********** name_list: {name_list}")
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
        if self.sendout_debug: print(names)
        return names

if __name__ == "__main__":
    if len(sys.argv)>=2:
        bib_manager(sys.argv[1])
    else:
        bib_manager()

import re
import pickle

class sent:
    def __init__(self, text, controller_id, app_title, SRL_labels):
        self.text = text.lower()
        self.token = []
        self.token_lemma = []
        self.pos_tag = []
        self.NER_label = {}
        self.tree = None
        self.SRL = None

        self.labels_practice = set()
        self.labels_fulfilled = set()
        self.labels_13_14 = set()

        self.action_predicate_list = []
        self.action_role_argument = []
        
        self.nlp = ''
        self.doc = ''
        self.SRL_predictor = ''
        self.controller_id = controller_id.lower()
        self.app_title = app_title.lower()

        self.passive_verb_list = []

        self.single_mode = ''
        self.SRL_labels = ''

        self.no_verb = True
        if SRL_labels == None:
            self.single_mode = True
        else:
            self.SRL_labels = SRL_labels


    def verb_practice_matching(self, verb):
        practices = []
        for action in self.action_predicate_list:
            if verb in action[1]:
                practices.append(action[0])
        if len(practices) != 0:
            return practices
        return False
    
    def predicate_extraction(self):
        f = open('meta_data/predicates.pickle', 'rb')
        predefined_predicates = pickle.load(f)

        for token in self.doc:
            self.token.append(token.text)
            self.token_lemma.append(token.lemma_)
            self.pos_tag.append(token.tag_)
            if 'VB' in token.tag_:
                self.no_verb = False
                for action, predicates in predefined_predicates.items():
                    if token.lemma_ in predicates:
                        self.action_predicate_list.append([action, token.text])
                if token.dep_ == 'auxpass':
                    self.passive_verb_list.append(token.head.text)
                
                if token.dep_ == 'conj' and token.head.text in self.passive_verb_list:
                    self.passive_verb_list.append(token.text)

    def get_semantic_roles_and_arguments(self):
        if self.single_mode:
            labels = self.SRL_predictor.predict(sentence = self.text)
            predicate_list = labels['verbs']
        else:
            predicate_list = self.SRL_labels['verbs']
        for predicate in predicate_list:
            verb_in_predicate = predicate['verb']
            practices = self.verb_practice_matching(verb_in_predicate)
            if practices:
                for practice in practices: 
                    description = predicate['description']
                    arguments = re.findall('\[.*?\]',description)
                    roles_and_arguments = []

                    for argument in arguments:
                        argument_split = argument.split(':')
                        roles = argument_split[0].replace('[', '')
                        arguments_phrase = ''.join(argument_split[1 : None]).replace(']', '')
                        roles_and_arguments.append([roles, arguments_phrase])
                    if [practice, roles_and_arguments] not in self.action_role_argument:
                        self.action_role_argument.append([practice, roles_and_arguments])

        return self.action_role_argument       

    def named_entity(self):
        CONTROLLER = ['we', 'i', 'me', 'us', 'developer', 'controller', 'owner', 'operator',
                      'this app', 'this application']
        USER = ['you', 'user', 'your', 'users']
        for ent in self.doc.ents:
            if len(ent) < 2 or (ent.text not in self.controller_id and ent.text not in self.app_title) :       
                self.NER_label[ent.text] = ent.label_
            else:
                self.NER_label[ent.text] = 'CONTROLLER'

        for token in self.doc:
            self.token.append(token.text)
            self.token_lemma.append(token.lemma_)
            self.pos_tag.append(token.tag_)
            if token.lemma_ in CONTROLLER or token.text in CONTROLLER:
                self.NER_label[token.text] = 'CONTROLLER'
        
            elif token.lemma_ in USER or token.text in USER:
                self.NER_label[token.text] = 'USER'

        return self.NER_label
    
    def set_ner(self, nlp):
        self.nlp = nlp
        self.doc = self.nlp(self.text)
    
    def set_srl(self, SRL_predictor):
        self.SRL_predictor = SRL_predictor

    def get_text(self):
        return self.text

    def get_passive_verb_list(self):
        return self.passive_verb_list

    def set_label_pratice(self, label):
        self.labels_practice.add(label)

    def set_label_fulfilled(self, label):
        self.labels_fulfilled.add(label)

    def set_label_13_14(self, label):
        self.labels_13_14.add(label)

    def get_label_pratice(self):
        return self.labels_practice
         
    def get_label_fulfilled(self):
        return self.labels_fulfilled
         
    def get_label_13_14(self):
        return self.labels_13_14

    def get_clean_text(self):
        return self.text

    def get_token(self):
        return self.token
    
    def get_token_lemma(self):
        return self.token_lemma
    
    def get_pos_tag(self):
        return self.pos_tag
    
    def get_NER_label(self):
        return self.NER_label
    
    def get_Dtree(self):
        return self.tree
    
    def get_SRL(self):
        return self.SRL


        
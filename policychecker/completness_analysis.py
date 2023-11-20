import json

class analyzer:
    def __init__(self, output_folder):
        self.S = set()
        self.S_legal = set()
        self.S_interest = set()
        self.P = set()
        self.invoke_13 = False
        self.invoke_14 = False
        self.mandatory_violations_count = 0
        self.art14_mandatory_violations_count = 0
        self.chain_violations_count = 0
        self.output = output_folder

        self.R_M = {"Controller identity",
            "Contact Information",
            "Data retention time limit",
            "Data retention criteria",
            "Data processing purpose",
            "legal basis",
            "Right to data access",
            "Right to data erasure",
            "Right to data rectification",
            "Right to restrict processing",
            "Right to object processing",
            "Right to data portability",
            "Right to lodge complaints"
            }


        self.R_M_14 = {
            'Categories of personal data',
            'Source of the personal data'
        }

        self.R_O = {
            "Interest pursued",
            "Right to withdraw consent",
            "Recipients of the personal data",
            "International data transfer behavior",
            "Adequacy decision",
            "Transfer safeguards",
            "Data collection necessity",
            "User obligation and consequences",
            "Automatic decision system in use",
            "Decision system logic",
            "System significance and impact",
        }

    def run(self, filename):
        fileid = filename.split('.')[0]
        reportJson = {'id': fileid, 'invoke_13': 0, 'invoke_14':0, 'mandatory_violations': [], 'art14_mandatory_violations':[], "logic_chain_violations": [], "legal basis":[]}
        
        if self.invoke_13:
            reportJson['invoke_13'] = 1
        if self.invoke_14:
            reportJson['invoke_14'] = 1

        mandatory_violations = self.R_M - self.S 
        if mandatory_violations:
            if 'Data retention time limit' in self.S or 'Data retention criteria' in self.S:
                if 'Data retention time limit'  in mandatory_violations:
                    mandatory_violations.remove('Data retention time limit')
                if 'Data retention criteria'  in mandatory_violations:
                    mandatory_violations.remove('Data retention criteria')
            if mandatory_violations:
                for mandatory_violation in mandatory_violations:
                    reportJson["mandatory_violations"].append(mandatory_violation)

        art14_mandatory_violations = self.R_M_14 - self.S 
        if self.invoke_14 and art14_mandatory_violations:
                for art14_mandatory_violation in art14_mandatory_violations:
                    reportJson["art14_mandatory_violations"].append(art14_mandatory_violation)


        if "user consent" in self.S_legal and "Right to withdraw consent" not in self.S:
            reportJson["logic_chain_violations"].append('consent chain violation')
            

        if "legitmate interest" in self.S_legal and "Interest pursued" not in self.S:
            reportJson["logic_chain_violations"].append('legitmate interest chain violation')
            
        
        if "International data transfer behavior" in self.S and ("Adequacy decision" not in self.S and "Transfer safeguards" not in self.S ):
            reportJson["logic_chain_violations"].append('data transfer chain violation')
    

        if self.invoke_13:
            if ("legal obligation" in self.S_legal or "performance contract" in self.S_legal) and 'User obligation and consequences' not in self.S:
                reportJson["logic_chain_violations"].append('User obligation chain violation')
        
        
        if 'data sharing' in self.P and 'Recipients of the personal data' not in self.S:
            reportJson["logic_chain_violations"].append('data sharing chain violation')

        if self.S_legal:
            for l in self.S_legal:
                reportJson["legal basis"].append(l)

        with open(self.output+ fileid +'_report.json', 'w') as f:
            json.dump(reportJson, f)
    
    def get_mandatory_violations_count(self):
        return self.mandatory_violations_count

    def get_art14_mandatory_violations_count(self):
        return self.art14_mandatory_violations_count
    
    def get_chain_violations_count(self):
        return self.chain_violations_count

    def set_S(self, item):
        self.S.add(item)
    
    def get_S(self):
        return self.S

    def set_S_legal(self, item):
        self.S_legal.add(item)

    def set_S_interest(self, item):
        self.S_interest.add(item)

    def set_P(self, item):
        self.P.add(item)
    
    def set_13(self, bool):
        self.invoke_13 = bool

    def set_14(self, bool):
        self.invoke_14 = bool

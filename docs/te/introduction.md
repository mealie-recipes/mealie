# మీలీ (Mealie) పరిచయం 🍲

**Mealie** అనేది ఒక స్వీయ హోస్టింగ్ (Self-Hosted) వంటకాల నిర్వహణ మరియు పంచుకునే వేదిక.  
ఇది వినియోగదారులు తమ వంటకాలను సురక్షితంగా భద్రపరచి, వర్గీకరించి, ఇతరులతో పంచుకునేందుకు సహాయపడుతుంది.

---

## 🧾 ముఖ్య లక్షణాలు

- **సులభమైన ఇంటర్‌ఫేస్:** ఉపయోగించడానికి సులభమైన డిజైన్‌తో రూపొందించబడింది.  
- **రెసిపీ దిగుమతి:** వెబ్‌సైట్లు లేదా ఫైళ్ల నుండి వంటకాలను సులభంగా దిగుమతి చేసుకోవచ్చు.  
- **కుటుంబ పంచుకోవడం:** కుటుంబ సభ్యులతో లేదా స్నేహితులతో వంటకాలను పంచుకోవచ్చు.  
- **సురక్షిత నిల్వ:** మీ డేటా మీ సొంత సర్వర్‌లోనే భద్రంగా ఉంటుంది.  
- **బహుభాషా మద్దతు:** ఇప్పుడు తెలుగు సహా అనేక భాషల్లో అందుబాటులో ఉంది.  

---

## ⚙️ ఇన్‌స్టాలేషన్ మరియు హోస్టింగ్ దశలు 🏠

**Mealie ను స్వయంగా హోస్ట్ చేయడం చాలా సులభం.**  
క్రింద ఇచ్చిన దశలను అనుసరించండి 👇

---

### 🔹 దశ 1: Docker ను ఇన్‌స్టాల్ చేయడం (Ubuntu కోసం)

```bash
# పాత Docker ప్యాకేజీలు ఉంటే తొలగించండి
sudo apt remove docker docker-engine docker.io containerd runc -y

# సిస్టమ్ ప్యాకేజీలను నవీకరించండి
sudo apt update
sudo apt upgrade -y

# అవసరమైన ప్యాకేజీలు ఇన్‌స్టాల్ చేయండి
sudo apt install -y ca-certificates curl gnupg lsb-release

# Docker యొక్క GPG కీని జోడించండి
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Docker రిపాజిటరీని జోడించండి
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Docker Engine మరియు Compose ప్లగిన్‌ను ఇన్‌స్టాల్ చేయండి
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

git clone https://github.com/gellikeerthi/mealie.git
cd mealie
docker compose up -d
మీ బ్రౌజర్‌లో ఈ లింక్ ఓపెన్ చేయండి 👇
👉 http://localhost:9925
తెలుగు మాట్లాడే వినియోగదారులు కూడా స్వీయ హోస్టింగ్ టెక్నాలజీని సులభంగా అర్థం చేసుకోవడానికి
మరియు తమ సొంత సర్వర్‌లో ప్రాజెక్ట్‌లను అమలు చేయడానికి ఈ డాక్యుమెంట్ ఉపయోగపడుతుంది.

"""Hand-written source material for the synthetic data sets.

All text in this file was written by Claude (Anthropic) for this project and spot-checked
by the author. It is released with the repository under the same licence and can be shared freely.

Each entry is a (Swedish, English) pair. The English text is a translation of the Swedish text,
so the sv/en sets are parallel.
"""

# ---------------------------------------------------------------------------
# Open-ended prompts, part 1: topics x templates
# Topics are written as indirect questions so they fit every template grammatically.
# ---------------------------------------------------------------------------

OPEN_TEMPLATES = [
    ("Förklara {x}.", "Explain {x}."),
    ("Kan du förklara {x} för en tolvåring?", "Can you explain {x} to a twelve-year-old?"),
    ("Beskriv kort {x}.", "Briefly describe {x}."),
    ("Skriv ett kort stycke om {x}.", "Write a short paragraph about {x}."),
    ("Jag har aldrig riktigt förstått {x}. Kan du hjälpa mig?",
     "I have never really understood {x}. Can you help me?"),
    ("Sammanfatta i tre punkter {x}.", "Summarize in three bullet points {x}."),
    ("Ge ett konkret exempel som visar {x}.", "Give a concrete example that shows {x}."),
    ("Vad är det viktigaste att veta om {x}?", "What is the most important thing to know about {x}?"),
]

OPEN_TOPICS = [
    ("hur fotosyntesen fungerar", "how photosynthesis works"),
    ("varför himlen är blå", "why the sky is blue"),
    ("hur en värmepump fungerar", "how a heat pump works"),
    ("vad inflation är och varför den uppstår", "what inflation is and why it happens"),
    ("hur vaccin skyddar mot sjukdomar", "how vaccines protect against disease"),
    ("varför vi har årstider", "why we have seasons"),
    ("hur internet skickar data mellan datorer", "how the internet sends data between computers"),
    ("vad som skiljer ett virus från en bakterie", "what the difference is between a virus and a bacterium"),
    ("hur en demokrati fungerar", "how a democracy works"),
    ("varför löven byter färg på hösten", "why leaves change colour in autumn"),
    ("hur räntan på ett lån beräknas", "how the interest on a loan is calculated"),
    ("vad ett ekosystem är", "what an ecosystem is"),
    ("hur en elbil skiljer sig från en bensinbil", "how an electric car differs from a petrol car"),
    ("varför sömn är viktig för hälsan", "why sleep is important for health"),
    ("hur ett kylskåp håller maten kall", "how a refrigerator keeps food cold"),
    ("vad klimatförändringar innebär", "what climate change means"),
    ("hur jordbävningar uppstår", "how earthquakes happen"),
    ("varför vi får träningsvärk", "why we get sore muscles after exercise"),
    ("hur man skyddar sina lösenord", "how to keep your passwords safe"),
    ("vad en budget är och hur man gör en", "what a budget is and how to make one"),
    ("hur norrsken uppstår", "how the northern lights form"),
    ("varför havet är salt", "why the sea is salty"),
    ("hur en solcell gör el av solljus", "how a solar cell turns sunlight into electricity"),
    ("vad allemansrätten innebär", "what the Swedish right of public access means"),
    ("hur bin gör honung", "how bees make honey"),
    ("varför man ska källsortera", "why people should sort their waste for recycling"),
    ("hur en GPS vet var den är", "how a GPS knows where it is"),
    ("vad skillnaden mellan väder och klimat är", "what the difference between weather and climate is"),
    ("hur hjärtat pumpar blod", "how the heart pumps blood"),
    ("varför is flyter på vatten", "why ice floats on water"),
    ("hur aktier fungerar", "how shares work"),
    ("vad artificiell intelligens är", "what artificial intelligence is"),
    ("hur man lär sig ett nytt språk effektivt", "how to learn a new language effectively"),
    ("varför det blir mörkt så tidigt på vintern i Sverige", "why it gets dark so early in winter in Sweden"),
    ("hur jäst får bröd att jäsa", "how yeast makes bread rise"),
    ("vad en vulkan är", "what a volcano is"),
    ("hur blixtar uppstår", "how lightning forms"),
    ("varför vi behöver vitaminer", "why we need vitamins"),
    ("hur ett batteri lagrar energi", "how a battery stores energy"),
    ("vad riksdagen gör", "what the Swedish parliament does"),
    ("hur tidvatten uppstår", "how tides happen"),
    ("varför fåglar flyttar söderut på hösten", "why birds migrate south in autumn"),
    ("hur en mikrovågsugn värmer mat", "how a microwave oven heats food"),
    ("vad kryptering är", "what encryption is"),
    ("hur regnbågar bildas", "how rainbows form"),
    ("varför motion är bra för hjärnan", "why exercise is good for the brain"),
    ("hur skatter används i samhället", "how taxes are used in society"),
    ("vad en algoritm är", "what an algorithm is"),
    ("hur växter tar upp vatten", "how plants take up water"),
    ("varför vi glömmer saker", "why we forget things"),
    ("hur ett flygplan kan flyga", "how an aeroplane can fly"),
    ("vad biologisk mångfald är", "what biodiversity is"),
    ("hur man startar ett litet företag", "how to start a small business"),
    ("varför månen ser olika ut under en månad", "why the moon looks different over the course of a month"),
    ("hur kompostering fungerar", "how composting works"),
    ("vad en pandemi är", "what a pandemic is"),
    ("hur en dator lagrar information", "how a computer stores information"),
    ("varför vissa material leder ström", "why some materials conduct electricity"),
    ("hur antibiotika verkar", "how antibiotics work"),
    ("vad ett pensionssystem är", "what a pension system is"),
    ("hur vindkraft fungerar", "how wind power works"),
    ("varför vi har tidszoner", "why we have time zones"),
    ("hur man förbereder sig inför en anställningsintervju", "how to prepare for a job interview"),
    ("hur kroppen reglerar sin temperatur", "how the body regulates its temperature"),
    ("vad källkritik är", "what source criticism is"),
    ("hur ljud färdas genom luften", "how sound travels through the air"),
    ("varför det är viktigt att dricka vatten", "why it is important to drink water"),
    ("hur myror samarbetar", "how ants cooperate"),
    ("vad en kommun ansvarar för", "what a municipality is responsible for"),
    ("hur glas tillverkas", "how glass is made"),
    ("varför stjärnorna blinkar", "why the stars twinkle"),
    ("hur ett mobilnät fungerar", "how a mobile network works"),
]

# ---------------------------------------------------------------------------
# Open-ended prompts, part 2: stand-alone everyday requests
# (advice, writing tasks, creative tasks, planning)
# ---------------------------------------------------------------------------

OPEN_STANDALONE = [
    ("Ge mig tre tips för att sova bättre.", "Give me three tips for sleeping better."),
    ("Skriv ett kort mejl till min chef där jag ber om ledigt på fredag.",
     "Write a short email to my manager asking for Friday off."),
    ("Föreslå en enkel middag som går att laga på tjugo minuter.",
     "Suggest a simple dinner that can be cooked in twenty minutes."),
    ("Skriv en kort dikt om hösten.", "Write a short poem about autumn."),
    ("Hur kan jag spara pengar på matinköpen?", "How can I save money on groceries?"),
    ("Planera en helgresa till Göteborg för två personer.", "Plan a weekend trip to Gothenburg for two people."),
    ("Vad ska jag tänka på när jag köper en begagnad cykel?",
     "What should I keep in mind when buying a used bicycle?"),
    ("Skriv en kort berättelse om en katt som går vilse i skogen.",
     "Write a short story about a cat that gets lost in the forest."),
    ("Ge mig några idéer på aktiviteter för en regnig söndag.",
     "Give me some ideas for activities on a rainy Sunday."),
    ("Hur kommer jag igång med att springa om jag aldrig har tränat?",
     "How do I get started with running if I have never exercised?"),
    ("Skriv en inbjudan till ett födelsedagskalas för min dotter som fyller sju år.",
     "Write an invitation to a birthday party for my daughter who is turning seven."),
    ("Vilka fördelar och nackdelar finns det med att jobba hemifrån?",
     "What are the advantages and disadvantages of working from home?"),
    ("Hjälp mig att skriva ett tack till en kollega som har hjälpt mig mycket.",
     "Help me write a thank-you note to a colleague who has helped me a lot."),
    ("Föreslå fem namn på ett litet kafé.", "Suggest five names for a small café."),
    ("Hur tar jag hand om en krukväxt som håller på att vissna?",
     "How do I care for a houseplant that is wilting?"),
    ("Skriv en kort produktbeskrivning för en vattentät ryggsäck.",
     "Write a short product description for a waterproof backpack."),
    ("Vad kan jag göra för att bli mindre stressad på jobbet?", "What can I do to feel less stressed at work?"),
    ("Ge mig ett recept på pannkakor.", "Give me a recipe for pancakes."),
    ("Hur förklarar jag för mitt barn varför man måste borsta tänderna?",
     "How do I explain to my child why we have to brush our teeth?"),
    ("Skriv ett kort tal till en väns bröllop.", "Write a short speech for a friend's wedding."),
    ("Vilka böcker passar för någon som vill börja läsa mer?",
     "Which books are good for someone who wants to start reading more?"),
    ("Hur kan jag göra min lägenhet mer energieffektiv?", "How can I make my flat more energy efficient?"),
    ("Skriv en kort recension av en påhittad restaurang.", "Write a short review of a made-up restaurant."),
    ("Ge mig tips på hur jag kan bli bättre på att hålla presentationer.",
     "Give me tips on how to get better at giving presentations."),
    ("Vad bör man packa inför en vandring i fjällen?", "What should you pack for a hike in the mountains?"),
    ("Skriv ett vänligt svar till en kund som klagar på en försenad leverans.",
     "Write a friendly reply to a customer who is complaining about a late delivery."),
    ("Hur planerar jag min vecka så att jag hinner med både jobb och träning?",
     "How do I plan my week so that I have time for both work and exercise?"),
    ("Föreslå en meny för en julmiddag för sex personer.", "Suggest a menu for a Christmas dinner for six people."),
    ("Skriv en rolig vers om en hund som älskar snö.", "Write a funny verse about a dog that loves snow."),
    ("Hur kan jag lära mig att laga mat från grunden?", "How can I learn to cook from scratch?"),
    ("Vilka frågor bör jag ställa när jag tittar på en lägenhet att hyra?",
     "What questions should I ask when I view a flat to rent?"),
    ("Skriv en kort annons för att sälja en begagnad soffa.", "Write a short ad to sell a used sofa."),
    ("Ge mig tre argument för att cykla till jobbet.", "Give me three arguments for cycling to work."),
    ("Hur hanterar jag en konflikt med en granne?", "How do I handle a conflict with a neighbour?"),
    ("Skriv en kort saga om en drake som är rädd för eld.",
     "Write a short fairy tale about a dragon that is afraid of fire."),
    ("Hur kan jag motivera mig själv att plugga inför en tenta?",
     "How can I motivate myself to study for an exam?"),
    ("Föreslå en dagsplan för en turist i Stockholm.", "Suggest a day plan for a tourist in Stockholm."),
    ("Skriv ett mejl där jag tackar nej till ett jobberbjudande.", "Write an email declining a job offer."),
    ("Vad är ett bra sätt att börja meditera?", "What is a good way to start meditating?"),
    ("Hur gör jag en enkel tomatsoppa?", "How do I make a simple tomato soup?"),
    ("Skriv en kort text om varför läsning är viktigt för barn.",
     "Write a short text about why reading is important for children."),
    ("Ge mig råd om hur jag kan bli mer organiserad.", "Give me advice on how to become more organised."),
    ("Hur ska jag tänka när jag väljer ett gymkort?", "How should I think when choosing a gym membership?"),
    ("Skriv en kort hälsning till en vän som har flyttat utomlands.",
     "Write a short greeting to a friend who has moved abroad."),
    ("Vad kan man göra med rester av kokt ris?", "What can you do with leftover cooked rice?"),
    ("Föreslå några sätt att minska min skärmtid.", "Suggest some ways to reduce my screen time."),
    ("Skriv en kort beskrivning av en vinterdag på landet.",
     "Write a short description of a winter day in the countryside."),
    ("Hur förbereder jag mig inför mitt första maraton?", "How do I prepare for my first marathon?"),
    ("Ge mig idéer på en present till min mormor som fyller åttio.",
     "Give me ideas for a present for my grandmother who is turning eighty."),
    ("Skriv ett kort inlägg till föreningens hemsida om vårens städdag.",
     "Write a short post for the association's website about the spring clean-up day."),
    ("Hur kan jag bli bättre på att lyssna på andra?", "How can I become a better listener?"),
    ("Vad bör jag göra innan jag åker på semester?", "What should I do before I go on holiday?"),
    ("Skriv en kort dialog mellan en kund och en bagare.", "Write a short dialogue between a customer and a baker."),
    ("Hur får jag mina barn att äta mer grönsaker?", "How can I get my children to eat more vegetables?"),
    ("Föreslå tre enkla övningar som man kan göra vid skrivbordet.",
     "Suggest three simple exercises you can do at your desk."),
    ("Skriv en kort motivering till varför jag söker ett jobb som lärare.",
     "Write a short statement about why I am applying for a job as a teacher."),
    ("Hur kan jag ta bättre bilder med mobilen?", "How can I take better photos with my phone?"),
    ("Vad ska man tänka på innan man skaffar hund?", "What should you consider before getting a dog?"),
    ("Skriv en kort text där jag presenterar mig själv på ett nytt jobb.",
     "Write a short text introducing myself at a new job."),
    ("Ge mig ett förslag på en veckomatsedel.", "Give me a suggestion for a weekly meal plan."),
    ("Hur kan jag minska mitt matsvinn?", "How can I reduce my food waste?"),
    ("Skriv en kort ursäkt till en vän för att jag glömde hennes födelsedag.",
     "Write a short apology to a friend for forgetting her birthday."),
    ("Vad är ett bra sätt att lära sig spela gitarr?", "What is a good way to learn to play the guitar?"),
    ("Föreslå några roliga lekar för ett barnkalas.", "Suggest some fun games for a children's party."),
    ("Skriv en kort nyhetstext om att ett nytt bibliotek öppnar i en liten stad.",
     "Write a short news item about a new library opening in a small town."),
    ("Hur kan jag förbättra min hållning?", "How can I improve my posture?"),
    ("Vilka växter är lätta att odla på en balkong?", "Which plants are easy to grow on a balcony?"),
    ("Skriv ett kort brev till mitt framtida jag.", "Write a short letter to my future self."),
    ("Hur kan jag säga nej till extra arbetsuppgifter på ett artigt sätt?",
     "How can I politely say no to extra tasks at work?"),
    ("Ge mig tips för att hålla mig varm under en kall vinter.",
     "Give me tips for keeping warm during a cold winter."),
    ("Skriv en kort beskrivning av en drömsemester.", "Write a short description of a dream holiday."),
    ("Hur kan jag hjälpa en vän som känner sig ensam?", "How can I help a friend who feels lonely?"),
    ("Föreslå ett upplägg för en bokcirkel.", "Suggest a format for a book club."),
    ("Skriv några rader om varför du tycker om sommaren.", "Write a few lines about why you like summer."),
]

# ---------------------------------------------------------------------------
# Math word problems: templates with a numeric answer.
# Each entry: (id, Swedish template, English template, sampler)
# The sampler returns (fields_dict, integer_answer) given a random.Random instance.
# ---------------------------------------------------------------------------


def _t_add(r):
    a, b = r.randint(3, 40), r.randint(2, 30)
    return dict(a=a, b=b), a + b


def _t_sub(r):
    a = r.randint(18, 34)
    b = r.randint(2, 9)
    return dict(a=a, b=b), a - b


def _t_mul(r):
    a, b = r.randint(4, 24), r.randint(2, 12)
    return dict(a=a, b=b), a * b


def _t_div(r):
    b, q = r.randint(2, 9), r.randint(5, 60)
    return dict(a=b * q, b=b), q


def _t_train(r):
    a, b = r.choice([60, 70, 80, 90, 100, 120, 150]), r.randint(2, 6)
    return dict(a=a, b=b), a * b


def _t_discount(r):
    a = r.choice([199, 249, 299, 349, 399, 450, 500, 600])
    b = r.choice([20, 30, 50, 75, 100, 120])
    return dict(a=a, b=b), a - b


def _t_bus(r):
    a, b = r.randint(15, 45), r.randint(2, 12)
    c = r.randint(1, 15)
    return dict(a=a, b=b, c=c), a - b + c


def _t_change(r):
    a, b = r.randint(2, 6), r.choice([12, 15, 18, 22, 25, 28, 35])
    c = 100 if a * b < 100 else 200
    if a * b >= 200:
        c = 500
    return dict(a=a, b=b, c=c), c - a * b


def _t_legs(r):
    a, b = r.randint(2, 15), r.randint(2, 15)
    return dict(a=a, b=b), 4 * (a + b)


def _t_age(r):
    a, b = r.randint(5, 16), r.randint(22, 40)
    return dict(a=a, b=b), a + b


def _t_buses_needed(r):
    b = r.choice([20, 25, 30, 40, 45, 50])
    a = r.randint(b + 1, 5 * b)
    if a % b == 0:
        a += 1
    return dict(a=a, b=b), -(-a // b)


def _t_pizza(r):
    b, c = r.randint(2, 4), r.randint(2, 3)
    a = r.choice([8, 10, 12, 16])
    while a - b * c < 0:
        b -= 1
    return dict(a=a, b=b, c=c), a - b * c


MATH_TEMPLATES = [
    ("add_apples",
     "Anna har {a} äpplen och köper {b} till. Hur många äpplen har hon nu?",
     "Anna has {a} apples and buys {b} more. How many apples does she have now?", _t_add),
    ("sub_class",
     "En klass har {a} elever. {b} av dem är sjuka i dag. Hur många elever är i skolan i dag?",
     "A class has {a} pupils. {b} of them are ill today. How many pupils are at school today?", _t_sub),
    ("mul_biscuits",
     "Ett paket innehåller {a} kakor. Hur många kakor finns det i {b} paket?",
     "A packet contains {a} biscuits. How many biscuits are there in {b} packets?", _t_mul),
    ("div_share",
     "{a} kronor ska delas lika mellan {b} personer. Hur många kronor får varje person?",
     "{a} kronor are to be shared equally between {b} people. How many kronor does each person get?", _t_div),
    ("mul_train",
     "Ett tåg kör {a} kilometer i timmen. Hur många kilometer kör det på {b} timmar?",
     "A train travels {a} kilometres per hour. How many kilometres does it travel in {b} hours?", _t_train),
    ("mul_pages",
     "Erik läser {a} sidor varje dag. Hur många sidor har han läst efter {b} dagar?",
     "Erik reads {a} pages every day. How many pages has he read after {b} days?", _t_mul),
    ("sub_discount",
     "En tröja kostar {a} kronor. Den sätts ned med {b} kronor. Vad kostar tröjan nu?",
     "A jumper costs {a} kronor. The price is reduced by {b} kronor. What does the jumper cost now?", _t_discount),
    ("mul_savings",
     "Lisa sparar {a} kronor i veckan. Hur många kronor har hon sparat efter {b} veckor?",
     "Lisa saves {a} kronor a week. How many kronor has she saved after {b} weeks?", _t_mul),
    ("bus_passengers",
     "En buss har {a} passagerare. Vid en hållplats går {b} av och {c} går på. Hur många passagerare finns det nu på bussen?",
     "A bus has {a} passengers. At a stop, {b} get off and {c} get on. How many passengers are on the bus now?", _t_bus),
    ("area_rect",
     "En rektangel är {a} meter lång och {b} meter bred. Hur stor är arean i kvadratmeter?",
     "A rectangle is {a} metres long and {b} metres wide. What is its area in square metres?", _t_mul),
    ("change_buns",
     "Johan köper {a} bullar för {b} kronor styck och betalar med en {c}-kronorssedel. Hur många kronor får han tillbaka?",
     "Johan buys {a} buns at {b} kronor each and pays with a {c}-kronor note. How many kronor does he get back?", _t_change),
    ("legs_farm",
     "En bonde har {a} kor och {b} får. Hur många ben har djuren tillsammans?",
     "A farmer has {a} cows and {b} sheep. How many legs do the animals have altogether?", _t_legs),
    ("age_father",
     "Sara är {a} år. Hennes pappa är {b} år äldre än hon. Hur gammal är hennes pappa?",
     "Sara is {a} years old. Her father is {b} years older than her. How old is her father?", _t_age),
    ("buses_needed",
     "{a} elever ska åka på utflykt. Varje buss har plats för {b} elever. Hur många bussar behövs?",
     "{a} pupils are going on a school trip. Each bus has room for {b} pupils. How many buses are needed?", _t_buses_needed),
    ("pizza_left",
     "En pizza delas i {a} bitar. {b} personer äter {c} bitar var. Hur många bitar blir kvar?",
     "A pizza is cut into {a} slices. {b} people eat {c} slices each. How many slices are left?", _t_pizza),
]

MATH_SUFFIX = ("Avsluta ditt svar med det slutliga talet.", "End your answer with the final number.")

# ---------------------------------------------------------------------------
# Reference paragraphs for perplexity (teacher-forced, no generation).
# ---------------------------------------------------------------------------

REF_PARAGRAPHS = [
    ("Stockholm är byggt på fjorton öar där Mälaren möter Östersjön. Staden har många parker, och på sommaren badar folk mitt i centrum. Kollektivtrafiken är väl utbyggd med tunnelbana, bussar och båtar.",
     "Stockholm is built on fourteen islands where Lake Mälaren meets the Baltic Sea. The city has many parks, and in summer people swim right in the centre. Public transport is extensive, with an underground, buses and boats."),
    ("Midsommar firas i slutet av juni och är en av årets största högtider i Sverige. Många samlas på landet, dansar runt midsommarstången och äter sill med färskpotatis. Ofta avslutas måltiden med jordgubbar och grädde.",
     "Midsummer is celebrated at the end of June and is one of the biggest holidays of the year in Sweden. Many people gather in the countryside, dance around the maypole and eat herring with new potatoes. The meal often ends with strawberries and cream."),
    ("Kanelbullar bakas av en jäst deg som fylls med smör, socker och kanel. Degen rullas ihop, skärs i bitar och gräddas tills bullarna är gyllenbruna. Den fjärde oktober firas kanelbullens dag.",
     "Cinnamon buns are made from a yeast dough filled with butter, sugar and cinnamon. The dough is rolled up, cut into pieces and baked until the buns are golden brown. Cinnamon Bun Day is celebrated on the fourth of October."),
    ("Fjällen i norra Sverige lockar vandrare från hela världen. Kungsleden sträcker sig över fyrtio mil mellan Abisko och Hemavan. Längs leden finns stugor där man kan övernatta.",
     "The mountains of northern Sweden attract hikers from all over the world. The King's Trail stretches over four hundred kilometres between Abisko and Hemavan. Along the trail there are huts where you can stay overnight."),
    ("Älgen är Sveriges största landdjur och kan väga över femhundra kilo. Den lever främst i skogen och äter blad, kvistar och vattenväxter. Varje höst jagas älg i stora delar av landet.",
     "The elk is Sweden's largest land animal and can weigh more than five hundred kilos. It lives mainly in the forest and eats leaves, twigs and water plants. Every autumn elk are hunted in large parts of the country."),
    ("Allemansrätten ger alla rätt att vistas i naturen, även på mark som någon annan äger. Man får plocka bär och svamp och tälta en natt. Samtidigt måste man visa hänsyn mot djur, natur och markägare.",
     "The right of public access gives everyone the right to spend time in nature, even on land that someone else owns. You may pick berries and mushrooms and camp for one night. At the same time, you must show consideration for animals, nature and landowners."),
    ("Ett bibliotek är mer än en plats för böcker. Där kan man låna ljudböcker, läsa tidningar och använda datorer gratis. Många bibliotek ordnar också läsecirklar och sagostunder för barn.",
     "A library is more than a place for books. There you can borrow audiobooks, read newspapers and use computers for free. Many libraries also organise reading circles and story times for children."),
    ("Hösten är svampsäsong i de svenska skogarna. Kantareller och karljohansvamp hör till de mest eftertraktade. Den som plockar svamp bör vara säker på vilka arter som är ätliga.",
     "Autumn is mushroom season in the Swedish forests. Chanterelles and porcini are among the most sought after. Anyone who picks mushrooms should be sure which species are edible."),
    ("Lucia firas den trettonde december med ljus och sång. Luciatåget leds av Lucia, som bär en krona med ljus i håret. Efter henne går tärnor, stjärngossar och tomtar.",
     "Lucia is celebrated on the thirteenth of December with candles and song. The Lucia procession is led by Lucia, who wears a crown of candles in her hair. Behind her walk handmaidens, star boys and elves."),
    ("Vasaloppet är ett skidlopp på nio mil mellan Sälen och Mora. Loppet hålls varje år i mars och lockar tusentals deltagare. Det första loppet kördes år 1922.",
     "Vasaloppet is a ninety-kilometre ski race between Sälen and Mora. The race is held every year in March and attracts thousands of participants. The first race was held in 1922."),
    ("Vatten fryser till is vid noll grader Celsius. Is har lägre densitet än flytande vatten och flyter därför. Det gör att sjöar fryser uppifrån och att fiskar kan överleva vintern.",
     "Water freezes into ice at zero degrees Celsius. Ice has a lower density than liquid water and therefore floats. This means that lakes freeze from the top down and that fish can survive the winter."),
    ("Hjärtat är en muskel som pumpar blod genom kroppen. Hos en vuxen människa slår det ungefär sjuttio gånger i minuten i vila. Blodet för syre och näring till alla celler.",
     "The heart is a muscle that pumps blood through the body. In an adult it beats about seventy times a minute at rest. The blood carries oxygen and nutrients to every cell."),
    ("Solen är en stjärna som till största delen består av väte och helium. Ljuset från solen tar ungefär åtta minuter att nå jorden. Utan solens energi skulle inget liv kunna finnas här.",
     "The sun is a star made up mostly of hydrogen and helium. Light from the sun takes about eight minutes to reach the earth. Without the sun's energy, no life could exist here."),
    ("Bin är viktiga för pollineringen av många växter. När de samlar nektar för de med sig pollen från blomma till blomma. Utan bin skulle skördarna av frukt och bär bli mycket mindre.",
     "Bees are important for the pollination of many plants. When they collect nectar, they carry pollen from flower to flower. Without bees, the harvests of fruit and berries would be much smaller."),
    ("En dator består av en processor, ett arbetsminne och en lagringsenhet. Processorn utför beräkningar, medan arbetsminnet håller de data som används just nu. Program och filer sparas på lagringsenheten.",
     "A computer consists of a processor, working memory and a storage device. The processor performs calculations, while the working memory holds the data that is being used right now. Programs and files are saved on the storage device."),
    ("Regn bildas när vattenånga i luften kyls ned och kondenserar till små droppar. Dropparna slås ihop till större droppar som blir för tunga för att sväva. Då faller de ned som regn.",
     "Rain forms when water vapour in the air cools and condenses into small droplets. The droplets merge into larger drops that become too heavy to float. Then they fall as rain."),
    ("Att cykla till jobbet är bra både för hälsan och för miljön. Det ger motion varje dag och minskar utsläppen från trafiken. I många städer byggs nya cykelbanor för att fler ska välja cykeln.",
     "Cycling to work is good for both your health and the environment. It gives you exercise every day and reduces emissions from traffic. In many cities new cycle lanes are being built so that more people will choose the bicycle."),
    ("Kaffe är en av de populäraste dryckerna i Sverige. Många tar en fikapaus både på förmiddagen och på eftermiddagen. Fikat är ofta ett tillfälle att prata med kollegor.",
     "Coffee is one of the most popular drinks in Sweden. Many people take a coffee break both in the morning and in the afternoon. The coffee break is often a chance to talk with colleagues."),
    ("Norrsken uppstår när laddade partiklar från solen träffar atmosfären. Ljuset syns oftast som gröna band på himlen. I norra Sverige kan man se norrsken under de mörka vintermånaderna.",
     "The northern lights form when charged particles from the sun hit the atmosphere. The light usually appears as green bands across the sky. In northern Sweden you can see the northern lights during the dark winter months."),
    ("Gotland är Sveriges största ö och ligger mitt i Östersjön. Visby är känt för sin medeltida ringmur. Under sommaren besöks ön av många turister.",
     "Gotland is Sweden's largest island and lies in the middle of the Baltic Sea. Visby is known for its medieval town wall. In summer the island is visited by many tourists."),
    ("En bra frukost ger energi inför dagen. Gröt, smörgåsar och frukt är vanliga val. Många dricker också ett glas mjölk eller juice.",
     "A good breakfast gives you energy for the day. Porridge, sandwiches and fruit are common choices. Many people also drink a glass of milk or juice."),
    ("Skolan i Sverige är obligatorisk från sex års ålder. Grundskolan pågår i nio år efter förskoleklassen. Därefter väljer de flesta att gå vidare till gymnasiet.",
     "School in Sweden is compulsory from the age of six. Compulsory school lasts nine years after the preschool class. After that, most pupils choose to go on to upper secondary school."),
    ("Tåget är ett bekvämt sätt att resa mellan svenska städer. Resan mellan Stockholm och Göteborg tar ungefär tre timmar. Under resan kan man arbeta, läsa eller titta ut genom fönstret.",
     "The train is a comfortable way to travel between Swedish cities. The journey between Stockholm and Gothenburg takes about three hours. During the journey you can work, read or look out of the window."),
    ("Granen är ett av de vanligaste träden i de svenska skogarna. Den behåller sina barr hela året. Till jul tar många in en gran och klär den med ljus och kulor.",
     "The spruce is one of the most common trees in the Swedish forests. It keeps its needles all year round. At Christmas many people bring a spruce indoors and decorate it with lights and baubles."),
    ("Träning stärker både kroppen och hjärnan. Redan en promenad på trettio minuter om dagen kan göra skillnad. Det viktigaste är att hitta en aktivitet som man tycker om.",
     "Exercise strengthens both the body and the brain. Even a thirty-minute walk a day can make a difference. The most important thing is to find an activity that you enjoy."),
    ("Till pannkakor behövs mjöl, mjölk, ägg och en nypa salt. Smeten vispas slät och får vila en stund. Sedan steks pannkakorna i smör i en het stekpanna.",
     "For pancakes you need flour, milk, eggs and a pinch of salt. The batter is whisked until smooth and left to rest for a while. Then the pancakes are fried in butter in a hot frying pan."),
    ("Mobiltelefonen har förändrat hur vi kommunicerar. I dag kan vi skicka meddelanden, ringa videosamtal och betala med samma apparat. Samtidigt diskuteras hur mycket skärmtid som är rimligt.",
     "The mobile phone has changed how we communicate. Today we can send messages, make video calls and pay with the same device. At the same time, people discuss how much screen time is reasonable."),
    ("Under vintern blir dagarna mycket korta i norra Sverige. Längst i norr går solen inte upp alls under några veckor. Den perioden kallas polarnatt.",
     "In winter the days become very short in northern Sweden. In the far north the sun does not rise at all for a few weeks. That period is called the polar night."),
    ("Sommaren i Sverige är kort men ljus. I juni är det nästan ljust dygnet runt i stora delar av landet. Många tar semester i juli och åker till landet eller skärgården.",
     "Summer in Sweden is short but light. In June it is light almost around the clock in large parts of the country. Many people take their holiday in July and go to the countryside or the archipelago."),
    ("Återvinning gör att material kan användas igen. Glas, papper, metall och plast sorteras i olika kärl. På så sätt sparas både energi och råvaror.",
     "Recycling means that materials can be used again. Glass, paper, metal and plastic are sorted into different bins. In this way both energy and raw materials are saved."),
    ("Vulkaner bildas där smält berg från jordens inre tar sig upp till ytan. Vid ett utbrott kan lava, aska och gaser slungas ut. Island har flera aktiva vulkaner.",
     "Volcanoes form where molten rock from the earth's interior makes its way to the surface. During an eruption, lava, ash and gases can be thrown out. Iceland has several active volcanoes."),
    ("En hund behöver motion, mat och sällskap varje dag. Olika raser har olika behov av aktivitet. Innan man skaffar hund bör man fundera på om man har tillräckligt med tid.",
     "A dog needs exercise, food and company every day. Different breeds have different needs for activity. Before getting a dog, you should think about whether you have enough time."),
    ("Musik kan påverka vårt humör. Snabba låtar kan ge energi, medan lugn musik hjälper oss att slappna av. Många lyssnar på musik när de tränar eller pluggar.",
     "Music can affect our mood. Fast songs can give us energy, while calm music helps us relax. Many people listen to music when they exercise or study."),
    ("Potatisen kom till Sverige på sextonhundratalet men blev vanlig först senare. I dag är potatis en självklar del av husmanskosten. Den kan kokas, stekas, mosas eller bakas i ugnen.",
     "The potato came to Sweden in the seventeenth century but only became common later. Today potatoes are an obvious part of traditional home cooking. They can be boiled, fried, mashed or baked in the oven."),
    ("Ett vindkraftverk omvandlar vindens rörelse till elektricitet. Vingarna driver en generator i toppen av tornet. Vindkraften står för en växande del av Sveriges elproduktion.",
     "A wind turbine converts the movement of the wind into electricity. The blades drive a generator at the top of the tower. Wind power accounts for a growing share of Sweden's electricity production."),
    ("Sömn är nödvändig för att kroppen och hjärnan ska kunna återhämta sig. Vuxna behöver i regel mellan sju och nio timmars sömn per natt. Brist på sömn kan påverka koncentrationen.",
     "Sleep is necessary for the body and the brain to recover. Adults generally need between seven and nine hours of sleep a night. Lack of sleep can affect concentration."),
    ("Ekorren är ett vanligt djur i svenska skogar och parker. Den samlar nötter och kottar som den gömmer inför vintern. Den yviga svansen hjälper ekorren att hålla balansen.",
     "The squirrel is a common animal in Swedish forests and parks. It collects nuts and cones that it hides for the winter. Its bushy tail helps the squirrel keep its balance."),
    ("Riksdagen består av trehundrafyrtionio ledamöter. Den stiftar lagar och beslutar om statens budget. Val till riksdagen hålls vart fjärde år.",
     "The Swedish parliament has three hundred and forty-nine members. It makes laws and decides on the state budget. Elections to parliament are held every four years."),
    ("Havet runt Sveriges östkust är bräckt, det vill säga en blandning av salt och sött vatten. Östersjön är mycket mindre salt än Nordsjön. Därför kan både saltvattensfisk och sötvattensfisk leva där.",
     "The sea along Sweden's east coast is brackish, that is, a mix of salt and fresh water. The Baltic Sea is much less salty than the North Sea. That is why both saltwater and freshwater fish can live there."),
    ("Att lära sig ett nytt språk tar tid. Det hjälper att lyssna, läsa och prata lite varje dag. Misstag är en naturlig del av lärandet.",
     "Learning a new language takes time. It helps to listen, read and speak a little every day. Mistakes are a natural part of learning."),
    ("Ost är en viktig del av den svenska frukosten. Västerbottensost och prästost är två kända sorter. Osten skärs ofta i tunna skivor med en osthyvel.",
     "Cheese is an important part of the Swedish breakfast. Västerbotten cheese and priest cheese are two well-known varieties. The cheese is often cut into thin slices with a cheese slicer."),
    ("Hösten börjar när temperaturen sjunker och dagarna blir kortare. Löven på lövträden skiftar i gult, orange och rött. Till slut faller de till marken inför vintern.",
     "Autumn begins when the temperature drops and the days get shorter. The leaves on the deciduous trees turn yellow, orange and red. In the end they fall to the ground before winter."),
    ("Elbilar blir allt vanligare på svenska vägar. De drivs av ett batteri som laddas från elnätet. En elbil släpper inte ut några avgaser medan den körs.",
     "Electric cars are becoming more and more common on Swedish roads. They are powered by a battery that is charged from the grid. An electric car does not emit any exhaust while it is being driven."),
    ("Den svenska skärgården består av tusentals öar och skär. Många har sommarstugor där och tar sig dit med båt. På vintern kan isen ibland bära så att man kan åka skridskor mellan öarna.",
     "The Swedish archipelago consists of thousands of islands and skerries. Many people have summer cottages there and get there by boat. In winter the ice can sometimes be thick enough to skate between the islands."),
    ("Fotosyntes är processen där växter omvandlar ljus, vatten och koldioxid till socker. Som en biprodukt bildas syre. Därför är växterna avgörande för livet på jorden.",
     "Photosynthesis is the process in which plants convert light, water and carbon dioxide into sugar. Oxygen is formed as a by-product. That is why plants are essential for life on earth."),
    ("Ett hushåll kan spara mycket energi genom små förändringar. Att sänka inomhustemperaturen med en grad gör skillnad. Det hjälper också att släcka lamporna i rum som inte används.",
     "A household can save a lot of energy through small changes. Lowering the indoor temperature by one degree makes a difference. It also helps to switch off the lights in rooms that are not in use."),
    ("Ett äpple om dagen sägs hålla doktorn borta. Äpplen innehåller fibrer och C-vitamin. I Sverige odlas många sorter, till exempel Ingrid Marie och Aroma.",
     "An apple a day is said to keep the doctor away. Apples contain fibre and vitamin C. Many varieties are grown in Sweden, for example Ingrid Marie and Aroma."),
    ("Ett mejl till en arbetsgivare bör vara tydligt och artigt. Börja med en hälsning och förklara kort vad ärendet gäller. Avsluta med ett vänligt tack och ditt namn.",
     "An email to an employer should be clear and polite. Start with a greeting and briefly explain what the matter concerns. End with a friendly thank you and your name."),
    ("Göteborg är Sveriges näst största stad och ligger på västkusten. Hamnen är den största i Norden. Staden är känd för sina spårvagnar och för fiskhallen Feskekôrka.",
     "Gothenburg is Sweden's second largest city and lies on the west coast. Its port is the largest in the Nordic countries. The city is known for its trams and for the fish market hall Feskekôrka."),
    ("Snö består av små iskristaller som bildas i molnen. Varje snöflinga har sex armar men ser ändå unik ut. Nysnö isolerar marken och skyddar växterna mot kyla.",
     "Snow consists of small ice crystals that form in the clouds. Every snowflake has six arms but still looks unique. Fresh snow insulates the ground and protects plants against the cold."),
]

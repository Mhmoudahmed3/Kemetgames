"""
Script to build the comprehensive 1,800-question QA dataset:
6 categories x 300 questions (100 easy, 100 mid, 100 hard) = 1,800 total.
Categories:
  - War
  - History
  - Science
  - Logic & Pattern IQ
  - General Knowledge
  - Tech & Pop Culture
"""

import json
import random
import sys
from pathlib import Path

_SCRIPT_DIR = str(Path(__file__).resolve().parent)
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from qa_general_data import GENERAL_EASY_EXTRA, GENERAL_HARD_EXTRA, GENERAL_MID_EXTRA
from qa_history_data import HISTORY_EASY_EXTRA, HISTORY_HARD_EXTRA, HISTORY_MID_EXTRA
from qa_logic_data import LOGIC_EASY_EXTRA, LOGIC_HARD_EXTRA, LOGIC_MID_EXTRA
from qa_science_data import SCIENCE_EASY_EXTRA, SCIENCE_HARD_EXTRA, SCIENCE_MID_EXTRA
from qa_tech_data import TECH_EASY_EXTRA, TECH_HARD_EXTRA, TECH_MID_EXTRA
from qa_war_data import WAR_EASY_EXTRA, WAR_HARD_EXTRA, WAR_MID_EXTRA

random.seed(42)  # Deterministic compilation

OUTPUT_FILE = Path(__file__).resolve().parent.parent / "data" / "qa_questions.json"


def make_q(cat, diff, q_text, correct, wrongs, explanation):
    options = list(wrongs[:3]) + [correct]
    random.shuffle(options)
    return {
        "category": cat,
        "difficulty": diff,
        "question": q_text,
        "options": options,
        "correct_index": options.index(correct),
        "explanation": explanation,
    }


def build_war_questions():
    questions = []

    # EASY: 100 questions
    easy_data = [
        ("In which year did World War II officially end?", "1945", ["1944", "1946", "1939"], "World War II concluded with Axis surrender in 1945."),
        ("In which year did World War I begin?", "1914", ["1918", "1912", "1939"], "World War I erupted in July 1914 following the assassination of Archduke Franz Ferdinand."),
        ("What code name was given to the Allied invasion of Normandy in June 1944?", "Operation Overlord", ["Operation Barbarossa", "Operation Market Garden", "Operation Torch"], "Operation Overlord was the historic Allied D-Day amphibious landing in Normandy on June 6, 1944."),
        ("Which ancient Greek city-state fought against Athens in the Peloponnesian War?", "Sparta", ["Thebes", "Corinth", "Argos"], "Sparta and its Peloponnesian League defeated Athens after decades of conflict (431–404 BC)."),
        ("Who was the British Prime Minister for the majority of World War II?", "Winston Churchill", ["Neville Chamberlain", "Clement Attlee", "Anthony Eden"], "Winston Churchill served as UK Prime Minister from 1940 to 1945 leading the wartime coalition."),
        ("Which naval battle in 1942 is widely considered the turning point in the Pacific War?", "Battle of Midway", ["Battle of Coral Sea", "Battle of Leyte Gulf", "Battle of Guadalcanal"], "Midway dealt a catastrophic blow to the Imperial Japanese Navy, sinking 4 fleet carriers."),
        ("What year did the surprise attack on Pearl Harbor occur?", "1941", ["1940", "1942", "1945"], "Japan attacked Pearl Harbor on December 7, 1941, bringing the US into WWII."),
        ("Who commanded the French forces at the Battle of Austerlitz in 1805?", "Napoleon Bonaparte", ["Louis XIV", "Charles de Gaulle", "Marshal Ney"], "Austerlitz (Battle of the Three Emperors) was Napoleon's masterstroke victory."),
        ("What river did Julius Caesar famously cross in 49 BC, starting a Roman civil war?", "Rubicon", ["Tiber", "Danube", "Rhine"], "Caesar uttered 'Alea iacta est' (The die is cast) upon crossing the Rubicon."),
        ("Which two nations fought in the Hundred Years' War?", "England and France", ["France and Spain", "England and Germany", "Spain and Portugal"], "The conflict lasted intermittently from 1337 to 1453 over the French throne."),
        ("What war featured the famous Battle of Gettysburg in 1863?", "American Civil War", ["Revolutionary War", "War of 1812", "Spanish-American War"], "Gettysburg was the bloodiest battle of the American Civil War and the turning point in the East."),
        ("Which treaty officially ended World War I in 1919?", "Treaty of Versailles", ["Treaty of Paris", "Treaty of Ghent", "Treaty of Utrecht"], "The Treaty of Versailles imposed strict reparations on Germany and reshaped European borders."),
        ("Which Soviet city withstood an epic 872-day Axis siege during World War II?", "Leningrad", ["Stalingrad", "Moscow", "Kiev"], "The Siege of Leningrad (Saint Petersburg) caused immense civilian casualties between 1941 and 1944."),
        ("What was the name of the German air force during World War II?", "Luftwaffe", ["Wehrmacht", "Kriegsmarine", "Kaiserliche Marine"], "The Luftwaffe was Germany's aerial warfare service branch."),
        ("Which epic naval battle in 1805 secured British naval supremacy under Admiral Nelson?", "Battle of Trafalgar", ["Battle of the Nile", "Battle of Copenhagen", "Battle of Jutland"], "Lord Nelson defeated the combined Franco-Spanish fleets off Cape Trafalgar, dying in the victory."),
        ("What weapon revolutionized infantry combat with rifled barrels and minié balls in the 19th century?", "Rifled musket", ["Crossbow", "Matchlock", "Flintlock smoothbore"], "Rifled muskets dramatically increased range and accuracy during the Crimean and American Civil Wars."),
        ("What wooden construction was supposedly used by the Greeks to infiltrate Troy?", "Trojan Horse", ["Siege Tower", "Battering Ram", "Ballista"], "Virgil's Aeneid describes the giant hollow wooden horse concealing Greek warriors."),
        ("What was the line of concrete fortifications built by France before WWII along its German border?", "Maginot Line", ["Siegfried Line", "Hindenburg Line", "Mannerheim Line"], "The Maginot Line was bypassed when Germany invaded through the Ardennes forest in Belgium."),
        ("Which battle in 1942–1943 is famous for brutal house-to-house fighting on the Volga river?", "Battle of Stalingrad", ["Battle of Kursk", "Battle of Moscow", "Battle of Kharkov"], "Stalingrad saw the encirclement and destruction of the German 6th Army."),
        ("Who was the Supreme Allied Commander in Europe on D-Day, later becoming US President?", "Dwight D. Eisenhower", ["Douglas MacArthur", "George S. Patton", "Omar Bradley"], "General Eisenhower oversaw Operation Overlord before his 1952 election as 34th US President."),
    ]
    for q, c, w, e in easy_data:
        questions.append(make_q("War", "easy", q, c, w, e))

    # Add remaining easy war questions programmatically up to 100
    battles_easy = [
        ("Battle of Waterloo", "1815", ["1805", "1812", "1820"], "Napoleon was defeated by Wellington and Blücher at Waterloo in June 1815."),
        ("Battle of Hastings", "1066", ["1215", "1415", "1096"], "William the Conqueror defeated King Harold II, establishing Norman rule in England."),
        ("Battle of Marathon", "490 BC", ["480 BC", "431 BC", "334 BC"], "Athenians defeated the first Persian invasion of Greece at the plain of Marathon."),
        ("Battle of Thermopylae", "480 BC", ["490 BC", "450 BC", "323 BC"], "King Leonidas and his 300 Spartans made their legendary stand against Xerxes' Persian army."),
        ("Battle of Agincourt", "1415", ["1346", "1453", "1380"], "Henry V's English longbowmen achieved a decisive victory against the French nobility."),
        ("Attack on Pearl Harbor", "December 1941", ["June 1942", "May 1941", "August 1945"], "The Japanese raid brought the United States directly into World War II."),
        ("Battle of Britain", "1940", ["1939", "1941", "1944"], "The RAF successfully defended the United Kingdom against sustained Luftwaffe air attacks."),
        ("Fall of Constantinople", "1453", ["1204", "1492", "1517"], "Sultan Mehmed II captured the Byzantine capital using massive bronze siege cannons."),
        ("Battle of Yorktown", "1781", ["1776", "1783", "1777"], "Washington and Rochambeau forced General Cornwallis to surrender, effectively winning the American Revolution."),
        ("Battle of Bunker Hill", "1775", ["1776", "1781", "1770"], "Early Revolutionary War battle in Boston that demonstrated colonial militia resolve."),
    ]
    for b_name, year, w_years, expl in battles_easy:
        questions.append(make_q("War", "easy", f"In which year or era did the famous {b_name} take place?", year, w_years, expl))

    commanders_easy = [
        ("Alexander the Great", "Macedon", ["Rome", "Persia", "Egypt"], "Alexander created one of history's largest empires stretching from Greece to northwestern India."),
        ("Hannibal Barca", "Carthage", ["Gaul", "Rome", "Sparta"], "Hannibal led Carthaginian armies and war elephants across the Alps into Italy."),
        ("Sun Tzu", "China", ["Japan", "Korea", "Vietnam"], "Sun Tzu was an ancient Chinese military strategist credited with authoring 'The Art of War'."),
        ("George Washington", "Continental Army", ["British Redcoats", "French Navy", "Prussian Guard"], "Washington was Commander-in-Chief of the American Revolutionary forces."),
        ("Robert E. Lee", "Confederate Army of Northern Virginia", ["Union Army of the Potomac", "British Royal Marines", "French Foreign Legion"], "General Lee commanded the primary Confederate field army in the American Civil War."),
        ("Ulysses S. Grant", "Union Army", ["Confederate Army", "Mexican Army", "Spanish Fleet"], "Grant accepted Lee's surrender at Appomattox Court House in April 1865."),
        ("Erwin Rommel", "Afrika Korps", ["Panzer Lehr", "Luftwaffe Paratroopers", "Kriegsmarine"], "Known as the 'Desert Fox', Rommel led German armored units in North Africa."),
        ("George S. Patton", "US Third Army", ["US Fifth Fleet", "British Eighth Army", "Soviet Red Army"], "Patton was renowned for his aggressive armored breakthroughs across France and Germany."),
        ("Douglas MacArthur", "Pacific Theater", ["European Theater", "Atlantic Fleet", "Mediterranean Air Wing"], "MacArthur accepted the official Japanese surrender aboard the USS Missouri."),
        ("Horatio Nelson", "Royal Navy", ["French Imperial Fleet", "Spanish Armada", "Imperial Russian Navy"], "Vice-Admiral Nelson was Britain's most celebrated naval hero of the Napoleonic Wars."),
    ]
    for cmdr, nation, w_nats, expl in commanders_easy:
        questions.append(make_q("War", "easy", f"Which military force or empire was led by {cmdr}?", nation, w_nats, expl))

    # Pad remaining easy up to 100 with distinct military facts
    mil_facts_easy = [
        ("What military decoration is the highest award for valor in the United States?", "Medal of Honor", ["Silver Star", "Purple Heart", "Bronze Star"], "The Medal of Honor is presented by the President in the name of Congress for extraordinary valor."),
        ("Which British decoration is the highest award for gallantry in the face of the enemy?", "Victoria Cross", ["George Cross", "Military Cross", "Distinguished Service Order"], "The Victoria Cross was instituted by Queen Victoria in 1856."),
        ("What color beret is traditionally worn by United Nations Peacekeepers?", "Blue", ["Green", "Red", "Black"], "UN peacekeepers are universally identified by their distinctive baby-blue helmets and berets."),
        ("What is the military rank immediately above Captain in the US Army?", "Major", ["Lieutenant", "Colonel", "General"], "In the US Army rank structure: Lieutenant -> Captain -> Major -> Lieutenant Colonel -> Colonel."),
        ("What term describes a temporary cessation of hostilities agreed upon by opposing sides?", "Armistice", ["Blockade", "Annexation", "Surrender"], "An armistice (such as the Nov 11, 1918 armistice) suspends active fighting while terms are negotiated."),
        ("What famous code name was given to the secret American project that developed the first atomic bomb?", "Manhattan Project", ["Project Apollo", "Project Mercury", "Project Manhattan Blue"], "The Manhattan Project was led by J. Robert Oppenheimer and Major General Leslie Groves."),
        ("Which city was the first to be targeted by an atomic weapon in warfare on August 6, 1945?", "Hiroshima", ["Nagasaki", "Tokyo", "Osaka"], "The B-29 bomber Enola Gay dropped the 'Little Boy' atomic bomb on Hiroshima."),
        ("Which city was the second to be hit by an atomic bomb on August 9, 1945?", "Nagasaki", ["Hiroshima", "Kyoto", "Kobe"], "The B-29 'Bockscar' dropped the plutonium weapon 'Fat Man' on Nagasaki."),
        ("What type of military aircraft is designed primarily to engage and destroy enemy aircraft?", "Fighter", ["Bomber", "Transport", "Reconnaissance"], "Fighter aircraft specialize in air-to-air combat and air superiority."),
        ("What type of ship is designed to launch and recover aircraft from its flight deck?", "Aircraft Carrier", ["Battleship", "Cruiser", "Destroyer"], "Aircraft carriers serve as floating airfields and capital flagships of modern navies."),
    ]
    for q, c, w, e in mil_facts_easy:
        questions.append(make_q("War", "easy", q, c, w, e))

    for q, c, w, e in WAR_EASY_EXTRA:
        questions.append(make_q("War", "easy", q, c, w, e))
    assert len(questions) == 100, f"Expected 100 War easy, got {len(questions)}"

    # MID: 100 questions
    mid_topics = [
        ("What was the largest tank battle in military history, fought in July–August 1943?", "Battle of Kursk", ["Battle of Stalingrad", "Battle of the Bulge", "Battle of El Alamein"], "Kursk involved over 6,000 tanks and marked the definitive end of German offensive capability in the East."),
        ("Which 1944 German counter-offensive through the snowy Ardennes was the largest battle fought by the US Army in WWII?", "Battle of the Bulge", ["Battle of Hurtgen Forest", "Operation Market Garden", "Battle of Aachen"], "Also known as the Ardennes Counteroffensive, the Allied line bent but never broke."),
        ("What 1805 battle is considered Napoleon's tactical masterpiece, where he used the Pratzen Heights to shatter Austro-Russian forces?", "Battle of Austerlitz", ["Battle of Jena", "Battle of Borodino", "Battle of Leipzig"], "Napoleon feigned weakness on his right flank before driving through the allied center on the Pratzen Heights."),
        ("Which war (1853–1856) was fought in the Black Sea and made Florence Nightingale famous for modern nursing?", "Crimean War", ["Franco-Prussian War", "Boer War", "Balkan War"], "Britain, France, and the Ottoman Empire allied against the Russian Empire in the Crimean peninsula."),
        ("What was the name of the German strategic plan to defeat France quickly by sweeping through Belgium in 1914?", "Schlieffen Plan", ["Manstein Plan", "Plan XVII", "Guderian Directive"], "Drafted by Count Alfred von Schlieffen, the plan aimed to knock out France before Russia mobilized."),
        ("Which 1942 naval battle was the first in history where the opposing ships never sighted or fired directly at each other?", "Battle of the Coral Sea", ["Battle of Midway", "Battle of Leyte Gulf", "Battle of the Java Sea"], "The entire engagement was fought exclusively by carrier-based aircraft."),
        ("What was the Allied airborne operation in September 1944 aimed at capturing bridges across the Rhine ('A Bridge Too Far')?", "Operation Market Garden", ["Operation Overlord", "Operation Dragoon", "Operation Husky"], "Market Garden captured several bridges but failed to secure the final bridge at Arnhem."),
        ("Which battle in 1709 saw Tsar Peter the Great decisively defeat King Charles XII of Sweden, ending Sweden's era as a great power?", "Battle of Poltava", ["Battle of Narva", "Battle of Gangut", "Battle of Fraustadt"], "Poltava established the Russian Empire as the dominant power in northern and eastern Europe."),
        ("What was the name of the German defense line in France during WWI, broken by the Allies in the Hundred Days Offensive?", "Hindenburg Line", ["Siegfried Line", "Maginot Line", "Mannerheim Line"], "The Siegfriedstellung (Hindenburg Line) was breached in late September 1918."),
        ("Which air-to-air missile was first used with deadly effect by British Harriers during the 1982 Falklands War?", "AIM-9L Sidewinder", ["AIM-7 Sparrow", "Exocet", "AMRAAM"], "The all-aspect AIM-9L allowed British Sea Harriers to engage Argentine jets head-on with devastating kill ratios."),
    ]
    for q, c, w, e in mid_topics:
        questions.append(make_q("War", "mid", q, c, w, e))

    # Add 90 more mid war questions with verified military milestones
    campaigns_mid = [
        ("Peninsular War", "1807–1814", ["1799–1802", "1815–1820", "1830–1836"], "Fought on the Iberian Peninsula, where British, Spanish, and Portuguese forces drained French imperial power."),
        ("Six-Day War", "1967", ["1973", "1956", "1982"], "A swift preemptive conflict in June 1967 involving Israel, Egypt, Jordan, and Syria."),
        ("Yom Kippur War", "1973", ["1967", "1982", "1956"], "Joint Arab surprise offensive across the Suez and Golan Heights on the Day of Atonement in October 1973."),
        ("Korean War Armistice", "1953", ["1950", "1955", "1948"], "The armistice at Panmunjom established the 38th parallel Demilitarized Zone (DMZ)."),
        ("Battle of Dien Bien Phu", "1954", ["1968", "1945", "1975"], "Viet Minh victory under General Giap forced the French evacuation of Indochina."),
        ("Tet Offensive", "1968", ["1965", "1972", "1975"], "Massive coordinated Viet Cong and North Vietnamese strike across South Vietnam during lunar new year."),
        ("Battle of Tsushima", "1905", ["1895", "1914", "1922"], "Admiral Togo's fleet annihilated the Russian Baltic Fleet, deciding the Russo-Japanese War."),
        ("Battle of Jutland", "1916", ["1914", "1918", "1915"], "The primary clash between British Grand Fleet dreadnoughts and the German High Seas Fleet."),
        ("Battle of Tannenberg", "1914", ["1916", "1917", "1918"], "Field Marshal Hindenburg and Ludendorff encircled and destroyed the Russian Second Army in East Prussia."),
        ("Battle of Gallipoli", "1915", ["1916", "1917", "1914"], "Allied amphibious landing on the Dardanelles peninsula defended successfully by Ottoman forces."),
    ]
    for c_name, yr, w_yrs, expl in campaigns_mid:
        questions.append(make_q("War", "mid", f"In which year or span was the {c_name} fought?", yr, w_yrs, expl))

    for q, c, w, e in WAR_MID_EXTRA:
        questions.append(make_q("War", "mid", q, c, w, e))
    assert len(questions) == 200, f"Expected 200 War up through mid, got {len(questions)}"

    # HARD: 100 questions
    hard_topics = [
        ("At which battle in 216 BC did Hannibal pull off history's classic double envelopment against 8 Roman legions?", "Battle of Cannae", ["Battle of Zama", "Battle of Trebia", "Battle of Lake Trasimene"], "Cannae remains the military gold standard of tactical encirclement and annihilation."),
        ("Which 1757 battle demonstrated Frederick the Great's use of the oblique order to defeat a superior Austrian army?", "Battle of Leuthen", ["Battle of Rossbach", "Battle of Zorndorf", "Battle of Kunersdorf"], "Frederick marched his army obliquely across the Austrian flank, crushing their line in detail."),
        ("What was the name of the German electro-mechanical rotor cipher machine broken by Marian Rejewski and Bletchley Park?", "Enigma", ["Lorenz SZ42", "SIGABA", "Purple"], "Polish cryptanalysts reconstructed Enigma's wiring before Alan Turing developed the bombe at Bletchley."),
        ("Which battle in 331 BC saw Alexander the Great defeat Darius III using a cavalry wedge aimed directly at the Persian King?", "Battle of Gaugamela", ["Battle of Issus", "Battle of the Granicus", "Battle of the Hydaspes"], "Alexander exploited an opening in the Persian battle line to charge directly at Darius."),
        ("What naval engagement in 480 BC saw the smaller Greek triremes defeat Xerxes' massive Persian fleet in narrow straits?", "Battle of Salamis", ["Battle of Artemision", "Battle of Mycale", "Battle of Lade"], "Themistocles lured the Persian fleet into the narrow waters between Salamis island and the mainland."),
        ("What 1813 engagement was known as the 'Battle of the Nations', involving over 600,000 soldiers and breaking Napoleon's control of Germany?", "Battle of Leipzig", ["Battle of Dresden", "Battle of Bautzen", "Battle of Lützen"], "Coalition armies converged on Leipzig, forcing Napoleon to retreat across the Rhine."),
        ("Which military treaty in 1648 concluded the devastating Thirty Years' War and established national sovereignty principles?", "Peace of Westphalia", ["Treaty of Utrecht", "Treaty of Tordesillas", "Peace of Augsburg"], "The treaties of Münster and Osnabrück fundamentally shaped modern international relations."),
        ("What was the name of the German 1941 surprise invasion of the Soviet Union, deploying over 3.8 million Axis personnel?", "Operation Barbarossa", ["Operation Typhoon", "Operation Citadel", "Operation Blue"], "Barbarossa opened the Eastern Front, the deadliest theater of conflict in human history."),
        ("What Roman general finally defeated Hannibal at the Battle of Zama in 202 BC?", "Scipio Africanus", ["Fabius Maximus", "Marcus Marcellus", "Lucius Paullus"], "Scipio adopted Hannibal's own tactics and used Numidian cavalry to seal the victory at Zama."),
        ("Which Byzantine secret weapon was an incendiary compound sprayed through siphons that burned on water?", "Greek Fire", ["Liquid Naphtha", "Quicklime Mortar", "Venetian Pitch"], "Greek Fire repeatedly saved Constantinople from naval sieges by Arab and Rus fleets."),
    ]
    for q, c, w, e in hard_topics:
        questions.append(make_q("War", "hard", q, c, w, e))

    for q, c, w, e in WAR_HARD_EXTRA:
        questions.append(make_q("War", "hard", q, c, w, e))
    assert len(questions) == 300, f"Expected 300 War total, got {len(questions)}"

    return questions


def build_category_questions(cat, easy_tuples, easy_extra, mid_tuples, mid_extra, hard_tuples, hard_extra):
    questions = []
    # 100 Easy
    for q, c, w, e in [*easy_tuples, *easy_extra]:
        questions.append(make_q(cat, "easy", q, c, w, e))
    assert len(questions) == 100, f"{cat} easy count {len(questions)} != 100"

    # 100 Mid
    for q, c, w, e in [*mid_tuples, *mid_extra]:
        questions.append(make_q(cat, "mid", q, c, w, e))
    assert len(questions) == 200, f"{cat} mid cumulative count {len(questions)} != 200"

    # 100 Hard
    for q, c, w, e in [*hard_tuples, *hard_extra]:
        questions.append(make_q(cat, "hard", q, c, w, e))
    assert len(questions) == 300, f"{cat} total count {len(questions)} != 300"

    return questions


def build_all_questions():
    all_qs = []

    # 1. WAR (300)
    print("Building War questions...")
    all_qs.extend(build_war_questions())

    # 2. HISTORY (300)
    print("Building History questions...")
    hist_easy = [
        ("Who was the first President of the United States?", "George Washington", ["Thomas Jefferson", "John Adams", "Benjamin Franklin"], "George Washington served from 1789 to 1797 after chairing the Constitutional Convention."),
        ("In which ancient civilization was the Great Pyramid of Giza constructed?", "Ancient Egypt", ["Mesopotamia", "Ancient Greece", "Roman Empire"], "Built for Pharaoh Khufu during the Fourth Dynasty around 2560 BC."),
        ("What year did Christopher Columbus first make landfall in the Americas?", "1492", ["1498", "1504", "1488"], "Columbus arrived in the Bahamas on October 12, 1492 sailing under the Spanish crown."),
        ("Which queen ruled Great Britain for over 63 years during the height of the Victorian Era?", "Queen Victoria", ["Queen Elizabeth I", "Queen Anne", "Queen Mary I"], "Victoria's reign from 1837 to 1901 oversaw vast industrial and imperial expansion."),
        ("What monumental wall in northern England was built by a Roman Emperor to protect Britannia?", "Hadrian's Wall", ["Antonine Wall", "Aurelian Wall", "Servian Wall"], "Emperor Hadrian ordered its construction in 122 AD across the width of northern England."),
        ("Which Renaissance polymath painted the Mona Lisa and The Last Supper?", "Leonardo da Vinci", ["Michelangelo", "Raphael", "Donatello"], "Leonardo da Vinci was the quintessential Italian Renaissance genius."),
        ("What famous document was signed by King John of England at Runnymede in 1215?", "Magna Carta", ["Bill of Rights", "Petition of Right", "Habeas Corpus Act"], "The Magna Carta established the principle that everyone, even the king, is subject to the law."),
        ("In what year did the French Revolution begin with the storming of the Bastille?", "1789", ["1799", "1776", "1804"], "The storming of the Bastille on July 14, 1789 ignited the French Revolution."),
        ("Which civilization built Machu Picchu in the Andes mountains of Peru?", "Inca", ["Aztec", "Maya", "Olmec"], "Machu Picchu was built in the 15th century as an estate for the Inca emperor Pachacuti."),
        ("What city was the capital of the Byzantine Empire for over a millennium?", "Constantinople", ["Athens", "Rome", "Alexandria"], "Founded by Constantine the Great in 330 AD on the site of ancient Byzantium."),
    ]
    hist_mid = [
        ("Which Chinese dynasty constructed the Forbidden City in Beijing?", "Ming Dynasty", ["Qing Dynasty", "Tang Dynasty", "Song Dynasty"], "Emperor Yongle of the Ming Dynasty moved the capital to Beijing and built the palace complex (1406–1420)."),
        ("What ancient Mesopotamian ruler created one of the earliest written legal codes?", "Hammurabi", ["Sargon of Akkad", "Nebuchadnezzar II", "Ashurbanipal"], "The Code of Hammurabi (c. 1750 BC) featured 282 edicts including 'an eye for an eye'."),
        ("Which empire was ruled by Suleiman the Magnificent in the 16th century?", "Ottoman Empire", ["Persian Empire", "Mughal Empire", "Safavid Empire"], "Suleiman expanded Ottoman territory across southeastern Europe, western Asia, and north Africa."),
        ("What revolution in 1868 brought an end to the Tokugawa shogunate in Japan?", "Meiji Restoration", ["Taika Reform", "Genpei War", "Satsuma Rebellion"], "The Meiji Restoration returned practical imperial rule and rapidly modernized Japan."),
        ("Which Mughal Emperor ordered the construction of the Taj Mahal as a mausoleum for his wife?", "Shah Jahan", ["Akbar the Great", "Babur", "Aurangzeb"], "Shah Jahan commissioned the white marble masterpiece for Mumtaz Mahal in 1632."),
    ]
    hist_hard = [
        ("Which 1356 decree issued by Emperor Charles IV fixed the election of the Holy Roman Emperor to seven prince-electors?", "Golden Bull of 1356", ["Edict of Worms", "Peace of Augsburg", "Concordat of Worms"], "The Golden Bull formed the constitutional framework of the Holy Roman Empire for over 400 years."),
        ("Which West African empire reached its zenith under Mansa Musa in the 14th century?", "Mali Empire", ["Songhai Empire", "Ghana Empire", "Kanem-Bornu Empire"], "Mansa Musa's 1324 pilgrimage to Mecca famously distributed so much gold it depressed gold prices in Cairo."),
        ("What treaty in 1494 divided newly discovered lands outside Europe between Portugal and the Crown of Castile?", "Treaty of Tordesillas", ["Treaty of Zaragoza", "Treaty of Madrid", "Treaty of Utrecht"], "The treaty drew a meridian 370 leagues west of the Cape Verde islands."),
        ("Who deciphered the Rosetta Stone in 1822, unlocking ancient Egyptian hieroglyphics?", "Jean-François Champollion", ["Thomas Young", "Heinrich Schliemann", "Howard Carter"], "Champollion used the bilingual Greek and cartouches of Ptolemy and Cleopatra to crack the script."),
        ("What Bronze Age civilization on the island of Crete is famous for the palace at Knossos?", "Minoan Civilization", ["Mycenaean Civilization", "Cycladic Civilization", "Hittite Empire"], "Minoans flourished from c. 2700 to 1450 BC before Mycenaean domination."),
    ]
    all_qs.extend(build_category_questions("History", hist_easy, HISTORY_EASY_EXTRA, hist_mid, HISTORY_MID_EXTRA, hist_hard, HISTORY_HARD_EXTRA))

    # 3. SCIENCE (300)
    print("Building Science questions...")
    sci_easy = [
        ("What chemical element has the symbol 'O' and atomic number 8?", "Oxygen", ["Osmium", "Gold", "Carbon"], "Oxygen makes up roughly 21% of Earth's atmosphere and is vital for aerobic respiration."),
        ("What is the center of an atom called?", "Nucleus", ["Electron", "Proton", "Neutron"], "The atomic nucleus contains protons and neutrons, orbited by electrons."),
        ("What planet is known as the 'Red Planet' due to iron oxide on its surface?", "Mars", ["Venus", "Jupiter", "Mercury"], "Mars appears reddish because of pervasive hematite (rust) on its surface."),
        ("What force pulls objects toward the center of the Earth?", "Gravity", ["Magnetism", "Friction", "Electromagnetism"], "Gravity is the attractive force that acts between all masses in the universe."),
        ("What biological process do green plants use to convert sunlight into glucose?", "Photosynthesis", ["Respiration", "Fermentation", "Transpiration"], "Chlorophyll captures light energy to turn water and carbon dioxide into sugars and oxygen."),
        ("What is the hardest known natural mineral on Earth?", "Diamond", ["Quartz", "Topaz", "Corundum"], "Diamond rates a 10 on the Mohs hardness scale because of its tetrahedral carbon crystal lattice."),
        ("How many chambers does the human heart have?", "4", ["2", "3", "6"], "The human heart consists of right and left atria and right and left ventricles."),
        ("What is the speed of light in a vacuum (rounded)?", "300,000 km/s", ["150,000 km/s", "500,000 km/s", "30,000 km/s"], "Light travels at exactly 299,792,458 meters per second in a vacuum."),
        ("What gas makes up approximately 78% of Earth's atmosphere?", "Nitrogen", ["Oxygen", "Carbon Dioxide", "Argon"], "Nitrogen (N2) is the most abundant gas in Earth's atmospheric envelope."),
        ("What molecule carries genetic instructions in all known living organisms?", "DNA", ["RNA", "Hemoglobin", "ATP"], "Deoxyribonucleic acid (DNA) forms the double helix discovered by Watson, Crick, and Franklin."),
    ]
    sci_mid = [
        ("What organelle is known as the powerhouse of the eukaryotic cell?", "Mitochondrion", ["Ribosome", "Endoplasmic Reticulum", "Golgi Apparatus"], "Mitochondria generate most of the chemical energy needed by the cell through ATP synthesis."),
        ("What law of thermodynamics states that entropy in an isolated system always increases over time?", "Second Law", ["First Law", "Third Law", "Zeroth Law"], "The Second Law dictates the direction of thermodynamic processes and the arrow of time."),
        ("What type of bond forms when atoms share pairs of electrons?", "Covalent Bond", ["Ionic Bond", "Hydrogen Bond", "Metallic Bond"], "Covalent bonding involves the mutual sharing of valence electrons between atoms."),
        ("What geological boundary is formed when tectonic plates slide past each other horizontally?", "Transform Fault", ["Convergent Boundary", "Divergent Boundary", "Subduction Zone"], "The San Andreas Fault in California is a premier example of a transform plate boundary."),
        ("What stellar remnant forms when a supermassive star undergoes gravitational collapse beyond neutron degeneracy?", "Black Hole", ["White Dwarf", "Neutron Star", "Pulsar"], "Black holes have an event horizon beyond which nothing, not even light, can escape."),
    ]
    sci_hard = [
        ("What quantum principle asserts that two identical fermions cannot occupy the same quantum state simultaneously?", "Pauli Exclusion Principle", ["Heisenberg Uncertainty", "Hund's Rule", "Aufbau Principle"], "Formulated by Wolfgang Pauli in 1925, it explains electron shell structure in chemistry."),
        ("What enzyme is responsible for synthesizing mRNA from a DNA template during transcription?", "RNA Polymerase", ["DNA Helicase", "DNA Ligase", "Topoisomerase"], "RNA polymerase unzips DNA and matches complementary RNA nucleotides."),
        ("What theoretical particle is proposed to mediate the gravitational interaction in quantum field theory?", "Graviton", ["Gluon", "W Boson", "Higgs Boson"], "The graviton is a hypothetical massless spin-2 boson in quantum gravity frameworks."),
        ("What geological epoch began approximately 11,700 years ago following the Last Glacial Period?", "Holocene", ["Pleistocene", "Pliocene", "Miocene"], "The Holocene encompasses the entire era of recorded human civilization."),
        ("What astronomical phenomenon causes the apparent shift in a star's position when viewed from opposite sides of Earth's orbit?", "Stellar Parallax", ["Aberration of Light", "Doppler Redshift", "Gravitational Lensing"], "Stellar parallax was first measured by Friedrich Bessel in 1838 for 61 Cygni."),
    ]
    all_qs.extend(build_category_questions("Science", sci_easy, SCIENCE_EASY_EXTRA, sci_mid, SCIENCE_MID_EXTRA, sci_hard, SCIENCE_HARD_EXTRA))

    # 4. LOGIC & PATTERN IQ (300)
    print("Building Logic & Pattern IQ questions...")
    iq_easy = [
        ("Which number completes the sequence: 2, 4, 8, 16, ___?", "32", ["24", "30", "64"], "Each term doubles the preceding number (16 * 2 = 32)."),
        ("Which number completes the sequence: 5, 10, 15, 20, ___?", "25", ["30", "22", "35"], "Each step adds 5: 20 + 5 = 25."),
        ("If all Roses are Flowers and all Flowers need Water, do all Roses need Water?", "Yes, definitely", ["No, never", "Only in summer", "Cannot be determined"], "By transitive syllogism: Roses -> Flowers -> Need Water."),
        ("What is the next prime number after 7?", "11", ["9", "10", "13"], "9 is divisible by 3, 10 is divisible by 2 and 5; 11 has only 1 and itself as factors."),
        ("A bat and a ball cost $1.10 in total. The bat costs $1.00 more than the ball. How much does the ball cost?", "$0.05 (5 cents)", ["$0.10 (10 cents)", "$0.01 (1 cent)", "$0.15 (15 cents)"], "Ball = $0.05, Bat = $1.05; Total = $1.10. Bat is exactly $1.00 more than the ball."),
        ("What letter comes next in the sequence: A, C, E, G, ___?", "I", ["H", "J", "K"], "Skips one letter each step (+2 letters in alphabet): A (+2) -> C (+2) -> E (+2) -> G (+2) -> I."),
        ("How many degrees are in the interior angles of a triangle?", "180°", ["90°", "360°", "270°"], "Euclidean triangle interior angles always sum to 180°."),
        ("Which word does not belong: Apple, Banana, Carrot, Orange?", "Carrot", ["Apple", "Banana", "Orange"], "Carrot is a root vegetable, whereas apple, banana, and orange are fruits."),
        ("If you rearrange the letters 'CIFAIPC', you get the name of a:", "Ocean (Pacific)", ["Country", "Animal", "City"], "PACIFIC is the world's largest ocean."),
        ("What is the square root of 144?", "12", ["14", "11", "16"], "12 * 12 = 144."),
    ]
    iq_mid = [
        ("What number completes the sequence: 2, 6, 12, 20, 30, ___?", "42", ["40", "44", "38"], "Deltas increase by 2 (+4, +6, +8, +10, +12): 30 + 12 = 42."),
        ("Which number completes the Fibonacci sequence: 1, 1, 2, 3, 5, 8, 13, ___?", "21", ["18", "20", "24"], "Each term is the sum of the two preceding terms: 8 + 13 = 21."),
        ("What is the probability of rolling a sum of 7 with two standard 6-sided dice?", "1/6 (6 in 36)", ["1/12", "1/8", "1/4"], "There are 6 winning pairs (1+6, 2+5, 3+4, 4+3, 5+2, 6+1) out of 36 outcomes: 6/36 = 1/6."),
        ("Complete the series: 3, 9, 27, 81, ___?", "243", ["162", "216", "324"], "Powers of 3 (3^1, 3^2, 3^3, 3^4, 3^5 = 243)."),
        ("If five machines take 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?", "5 minutes", ["100 minutes", "20 minutes", "1 minute"], "Each machine takes 5 minutes to produce 1 widget. Thus, 100 machines working in parallel take 5 minutes for 100 widgets."),
    ]
    iq_hard = [
        ("What number completes the sequence: 3, 5, 9, 17, 33, ___?", "65", ["64", "66", "49"], "Deltas double each step (+2, +4, +8, +16, +32): 33 + 32 = 65 (also 2^n + 1)."),
        ("On an island where Knights always tell the truth and Knaves always lie, person A says: 'We are both Knaves.' What is person A?", "A is a Knave", ["A is a Knight", "A is an Angel", "Paradox with no solution"], "If A were a Knight, the statement would be true, meaning A is a Knave (contradiction). Thus A is a Knave lying."),
        ("What is the remainder when 7^100 is divided by 5?", "1", ["2", "3", "4"], "Powers of 7 mod 5 cycle every 4: 7^1 = 2, 7^2 = 4, 7^3 = 3, 7^4 = 1. Since 100 is a multiple of 4, 7^100 = 1 (mod 5)."),
        ("How many non-overlapping diagonals can be drawn inside a regular hexagon?", "9", ["6", "12", "15"], "Formula for polygon diagonals: n(n - 3) / 2. For n=6: 6 * 3 / 2 = 9."),
        ("In a tournament of 64 players with single-elimination knockouts, how many total matches must be played to determine the champion?", "63", ["64", "32", "128"], "Every match eliminates exactly one player. To eliminate 63 players to leave 1 champion requires 63 matches."),
    ]
    all_qs.extend(build_category_questions("Logic & Pattern IQ", iq_easy, LOGIC_EASY_EXTRA, iq_mid, LOGIC_MID_EXTRA, iq_hard, LOGIC_HARD_EXTRA))

    # 5. GENERAL KNOWLEDGE (300)
    print("Building General Knowledge questions...")
    gen_easy = [
        ("What is the capital city of France?", "Paris", ["Lyon", "Marseille", "Bordeaux"], "Paris is the capital and largest city of France, situated along the Seine."),
        ("Which is the largest ocean on planet Earth?", "Pacific Ocean", ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean"], "The Pacific Ocean covers over 30% of Earth's total surface area."),
        ("Who wrote the classical play 'Romeo and Juliet'?", "William Shakespeare", ["Charles Dickens", "Jane Austen", "Mark Twain"], "William Shakespeare penned Romeo and Juliet early in his career in London around 1595."),
        ("How many days are in a leap year?", "366", ["365", "364", "367"], "A leap year adds February 29th, totaling 366 days to synchronize with Earth's orbit."),
        ("Which country is famous for the Eiffel Tower?", "France", ["Italy", "Spain", "Germany"], "The Eiffel Tower was constructed by Gustave Eiffel for the 1889 Paris World's Fair."),
        ("What is the largest land mammal in the world?", "African Elephant", ["White Rhinoceros", "Hippopotamus", "Giraffe"], "African bush elephants can weigh up to 6 metric tons and reach 4 meters at the shoulder."),
        ("What currency is used in Japan?", "Yen", ["Won", "Yuan", "Ringgit"], "The Yen (¥) is the official currency of Japan."),
        ("How many continents are there on Earth?", "7", ["5", "6", "8"], "The seven continents are Asia, Africa, North America, South America, Antarctica, Europe, and Australia."),
        ("What primary language is spoken in Brazil?", "Portuguese", ["Spanish", "French", "English"], "Brazil is the only Portuguese-speaking nation in the Americas."),
        ("What color is found at the top of a standard rainbow?", "Red", ["Violet", "Green", "Blue"], "Red has the longest wavelength in visible light and refracts at the top of the rainbow arc."),
    ]
    gen_mid = [
        ("What canal connects the Atlantic and Pacific oceans through Central America?", "Panama Canal", ["Suez Canal", "Kiel Canal", "Erie Canal"], "The 82-kilometer Panama Canal opened in 1914, drastically cutting maritime transit times."),
        ("Which author created the famous detective Sherlock Holmes?", "Arthur Conan Doyle", ["Agatha Christie", "Edgar Allan Poe", "Raymond Chandler"], "Sir Arthur Conan Doyle introduced Sherlock Holmes in 'A Study in Scarlet' (1887)."),
        ("What is the capital city of Australia?", "Canberra", ["Sydney", "Melbourne", "Brisbane"], "Canberra was chosen as a compromise capital between rivals Sydney and Melbourne in 1908."),
        ("What deep-sea trench is the deepest known location on Earth?", "Mariana Trench", ["Puerto Rico Trench", "Java Trench", "Tonga Trench"], "Challenger Deep in the Mariana Trench reaches approximately 10,994 meters (36,070 feet) depth."),
        ("Which Italian artist sculpted the marble statue of David in Florence?", "Michelangelo", ["Leonardo da Vinci", "Donatello", "Bernini"], "Michelangelo sculpted David between 1501 and 1504 from a single block of Carrara marble."),
    ]
    gen_hard = [
        ("Which sea on Earth has no terrestrial coastline, bounded only by four oceanic currents?", "Sargasso Sea", ["Baltic Sea", "Coral Sea", "Weddell Sea"], "The Sargasso Sea in the North Atlantic is bounded by the Gulf Stream, North Atlantic Current, Canary Current, and Atlantic Equatorial Current."),
        ("What is the only country in the world that is completely surrounded by South Africa?", "Lesotho", ["Eswatini", "Botswana", "Namibia"], "The Kingdom of Lesotho is an enclaved landlocked nation within South Africa."),
        ("Who wrote the landmark 19th-century epic novel 'War and Peace'?", "Leo Tolstoy", ["Fyodor Dostoevsky", "Anton Chekhov", "Ivan Turgenev"], "Leo Tolstoy published War and Peace in 1869 chronicling French invasion of Russia in 1812."),
        ("What ancient library in Egypt was one of the largest and most significant libraries of the ancient world?", "Library of Alexandria", ["Library of Pergamum", "Library of Celsus", "Villa of the Papyri"], "Founded under the Ptolemaic dynasty in the 3rd century BC as a major center of Hellenistic scholarship."),
        ("Which strait separates Spain from Morocco, linking the Atlantic to the Mediterranean?", "Strait of Gibraltar", ["Strait of Hormuz", "Bosphorus Strait", "Strait of Malacca"], "The Strait of Gibraltar narrows to 14.3 kilometers (8.9 miles) between Europe and Africa."),
    ]
    all_qs.extend(build_category_questions("General Knowledge", gen_easy, GENERAL_EASY_EXTRA, gen_mid, GENERAL_MID_EXTRA, gen_hard, GENERAL_HARD_EXTRA))

    # 6. TECH & POP CULTURE (300)
    print("Building Tech & Pop Culture questions...")
    tech_easy = [
        ("What company created the iPhone and Mac computers?", "Apple", ["Microsoft", "Google", "Samsung"], "Apple Inc. was co-founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976."),
        ("Which popular programming language is famous for its clean syntax and named after Monty Python?", "Python", ["Java", "C++", "Ruby"], "Guido van Rossum created Python and released it in 1991, naming it after Monty Python's Flying Circus."),
        ("What open-source operating system was created by Linus Torvalds in 1991?", "Linux", ["Windows", "FreeBSD", "Solaris"], "Linus Torvalds released the Linux kernel in 1991, now powering servers, Android, and supercomputers."),
        ("What does 'WWW' stand for in website addresses?", "World Wide Web", ["World Wide Wide", "Web World Wide", "Wild World Web"], "Tim Berners-Lee invented the World Wide Web in 1989 at CERN."),
        ("Which video game character is an Italian plumber with a red hat and mustache?", "Mario", ["Luigi", "Sonic", "Pac-Man"], "Mario was created by Shigeru Miyamoto and debuted in Donkey Kong (1981)."),
        ("What popular video game allows players to build and survive in a blocky 3D procedurally generated world?", "Minecraft", ["Roblox", "Terraria", "Fortnite"], "Minecraft was created by Markus 'Notch' Persson in 2009 and is the best-selling video game in history."),
        ("What company developed the Windows operating system?", "Microsoft", ["IBM", "Apple", "Oracle"], "Microsoft was founded by Bill Gates and Paul Allen in 1975."),
        ("What technology allows electronic devices to connect to wireless local area networks?", "Wi-Fi", ["Bluetooth", "Infrared", "Ethernet"], "Wi-Fi uses IEEE 802.11 standards to provide radio frequency network connectivity."),
        ("What does 'AI' stand for in computer science?", "Artificial Intelligence", ["Automated Interface", "Applied Integration", "Advanced Information"], "Artificial Intelligence focuses on building systems capable of performing tasks requiring human cognition."),
        ("Which web browser was created by Google and launched in 2008?", "Chrome", ["Firefox", "Safari", "Edge"], "Google Chrome is the most widely used web browser in the world."),
    ]
    tech_mid = [
        ("What British mathematician and cryptanalyst is considered the father of theoretical computer science and AI?", "Alan Turing", ["Charles Babbage", "John von Neumann", "Claude Shannon"], "Turing formalized computation with the Turing machine and broke the German Enigma code."),
        ("Who is widely recognized as the world's first computer programmer for writing an algorithm for Babbage's Analytical Engine?", "Ada Lovelace", ["Grace Hopper", "Katherine Johnson", "Margaret Hamilton"], "Ada Lovelace recognized in 1843 that computing machines could manipulate symbols beyond pure numbers."),
        ("What networking protocol is used to securely browse websites with encrypted TLS/SSL communication?", "HTTPS", ["HTTP", "FTP", "Telnet"], "HTTPS encrypts communications using Transport Layer Security to protect user data from eavesdropping."),
        ("In computer architecture, what type of high-speed memory sits directly on the CPU die between registers and RAM?", "Cache Memory (L1/L2/L3)", ["Virtual Memory", "ROM", "Hard Disk Buffer"], "CPU caches store frequently accessed instructions and data to minimize latency delays to main memory."),
        ("What data structure operates on a 'First-In, First-Out' (FIFO) basis?", "Queue", ["Stack", "Binary Search Tree", "Max Heap"], "A queue processes elements in the exact order they arrive, unlike a LIFO stack."),
    ]
    tech_hard = [
        ("What consensus algorithm, designed as a more understandable alternative to Paxos, is used in distributed systems like etcd?", "Raft", ["Byzantine Agreement", "Proof of Work", "Chord"], "Raft achieves distributed consensus via leader election, log replication, and safety invariants."),
        ("What asymmetric public-key cryptosystem relies on the computational difficulty of factoring the product of two large prime numbers?", "RSA", ["Diffie-Hellman", "AES", "SHA-256"], "Rivest, Shamir, and Adleman published RSA in 1977, forming the backbone of secure internet protocols."),
        ("What was the name of the first programmable, electronic, general-purpose digital computer completed in the United States in 1945?", "ENIAC", ["UNIVAC I", "Colossus", "Harvard Mark I"], "ENIAC was designed by John Mauchly and J. Presper Eckert at the University of Pennsylvania."),
        ("In compiler design, what intermediate tree representation depicts the abstract syntactic structure of source code?", "Abstract Syntax Tree (AST)", ["Control Flow Graph", "Parse Forest", "Bytecode Stack"], "Compilers parse source tokens into an AST before semantic analysis, optimization, and code generation."),
        ("What iconic 8-bit home computer released in 1982 holds the Guinness World Record for the highest-selling single computer model?", "Commodore 64", ["Apple II", "ZX Spectrum", "BBC Micro"], "The Commodore 64 sold an estimated 12.5 to 17 million units worldwide."),
    ]
    all_qs.extend(build_category_questions("Tech & Pop Culture", tech_easy, TECH_EASY_EXTRA, tech_mid, TECH_MID_EXTRA, tech_hard, TECH_HARD_EXTRA))

    return all_qs


def main():
    print("Compiling 1,800-question QA dataset...")
    questions = build_all_questions()

    print(f"Total compiled questions: {len(questions)}")
    cats = {}
    diffs = {}
    cat_diffs = {}

    seen_questions = set()
    banned_markers = (
        "Rule #",
        "Model #",
        "Mastery Axiom #",
        "Military Doctrine Item #",
        "Strategic Intelligence Milestone #",
        "Wait—",
    )

    for idx, q in enumerate(questions):
        cat = q["category"]
        diff = q["difficulty"]
        cats[cat] = cats.get(cat, 0) + 1
        diffs[diff] = diffs.get(diff, 0) + 1
        pair = (cat, diff)
        cat_diffs[pair] = cat_diffs.get(pair, 0) + 1

        assert len(q["options"]) == 4, f"Q {idx} does not have 4 options"
        assert 0 <= q["correct_index"] <= 3, f"Q {idx} invalid correct_index"
        assert q["options"][q["correct_index"]], f"Q {idx} correct option is empty"
        assert len(set(q["options"])) == 4, f"Q {idx} has duplicate options: {q['options']}"
        assert q["question"], f"Q {idx} question is empty"
        assert q["explanation"], f"Q {idx} explanation is empty"
        q_norm = q["question"].strip().lower()
        assert q_norm not in seen_questions, f"Duplicate question at {idx}: {q['question']}"
        seen_questions.add(q_norm)
        for marker in banned_markers:
            assert marker not in q["question"] and marker not in q["explanation"] and all(marker not in opt for opt in q["options"]), f"Placeholder/draft marker {marker!r} found at {idx}: {q['question']}"

    print("\nSummary by Category:")
    for c, count in cats.items():
        print(f"  - {c}: {count}")
        assert count == 300, f"Category {c} has {count} != 300 questions!"

    print("\nSummary by Difficulty:")
    for d, count in diffs.items():
        print(f"  - {d}: {count}")
        assert count == 600, f"Difficulty {d} has {count} != 600 questions!"

    print("\nSummary by (Category, Difficulty):")
    for (c, d), count in sorted(cat_diffs.items()):
        print(f"  - ({c}, {d}): {count}")
        assert count == 100, f"({c}, {d}) has {count} != 100 questions!"

    # Write out to backend/data/qa_questions.json
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully wrote 1,800 validated questions to {OUTPUT_FILE}!")


if __name__ == "__main__":
    main()


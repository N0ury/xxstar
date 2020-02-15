# xxstar
Utilisation d'un lecteur de glycémie bgstar ou Mystar sous Linux ou MacOs  

En 2016, je me suis retrouvé possesseur d'un lecteur de glycémie Mystar Extra, puis très vite j'ai commandé un BGStar.  
En effet la lecture des modes d'emploi m'a convaincu que le BGStar était meilleur.  
Je n'en suis plus tout à fait persuadé aujourd'hui.  
  
Le problème était que ces deux appareils sont utilisables avec des logiciels sous Windows seulement.  
Le logiciel de Sanofi lui n'est même pas utilisable sous Windows 10.  
Mais il existe d'autres logiciels, dont l'un des plus connus est SiDiary. Il reconnait un très grand nombre de lecteurs.    
  
Étant utilisateur de MacOs et de Linux, cette situation ne me convenait pas.  
  
J'ai donc branché le lecteur sous Linux. Il a été immédiatement reconnu.  
Les modules usbserial et cp210x ont été chargés, et le device /dev/ttyUSB0 a été créé.  
Sous Mac, rien. Aucune réaction.  
  
J'ai vu que le dispositif USB était un convertisseur USB-UART, comme sous Windows.  
De plus le composant utilisé fonctionne avec un driver CP210x de Silicon Labs.  
  
Donc pour Linux, il a fallu faire un travail de reverse engineering.  
Le câble de liaison pour relier le lecteur à un ordinateur n'est pas un simple cable. C'est là que se trouve l'adaptateur USB-UART. J'ai donc récupéré le vendor id et le product id, puis l'ai ajouté au driver pour Mac de Silicon Labs.  
Il a fonctionné, mais le driver n'était plus signé.  
J'ai donc gentiment demandé à Silicon Labs de faire le même ajout que moi sur leur driver.  
Miracle, ils ont accepté.  
Le driver disponible depuis reconnait le câble qui porte le nom de `Zero-Click`.  
Le firmware est conçu par Agamatrix.  
Sous Mac, le device /dev/cu.SLAB_USBtoUART est créé.  
  
Pour ceux que ça intéresserait, j'ai décrit le protocol [ici](https://github.com/glucometers-tech/glucometer-protocols/blob/master/sanofi/bgstar-mystar.md)  
  
Le programme est un script Python unique.  
  
La syntaxe d'utilisation est:  

```
xxstar.py [-d] [-s] [-u] [-a] [-h]  
-d: Debug mode. Permet d'afficher les requêtes et tout le contenu du lecteur avec les secondes  
    Ne tient pas compte du fichier xxstar.last, et ne le modifie pas  
-s: Simulation. Affiche toutes les mesures nouvelles, mais ne modifie pas xxstar.last  
-u: Update. Affiche toutes les mesures nouvelles, et modifie xxstar.last  
-a: All. Affiche toutes les mesures mais ne modifie pas xxstar.last  
-h: help  
  
-d et -s sont exclusifs l'un de l'autre  
```
Pour les modes `update` et `simulation`, seules les mesures récuérées depuis la dernière fois sont récuérées.  
Avec le mode `update`, le fichier `xxstar.last`est modifié. La date du dernier résultat récupéré y est stockée.  
Elle servira de référence pour la prochaine utilisation des modes `similation`ou `update`.  

Je ne me souviens plus s'il y a des choses à installer au préalable, mais il ne me semble pas.  
  
En cas de problème ou de question, ne pas hésiter à ouvrir une `issue`.  

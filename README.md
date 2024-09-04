# Wallex : le gestionnaire de wallets crypto

Wallex est un outil permettant de garder une vue d'ensemble sur ses cryptos.
Ses principales qualitées / fonctionnalités:

* Vue par wallet (graphique et textuelle):
  * total : affiche le total de chaque wallet
  * detaillée : affiche chaque token
  * par criteres perso : à l'aide de tags on peut afficher par strategies/ categories/ etc
  * des totaux historiques : total par wallet en USD pour le moment

Pour ce faire il y a:
* Un moteur de scraping(haha moteur 4 fonctions basics) qui prend en charge les blockchains EVM,SVM, EGLD, BTC qui renvoit le total du wallet cible.
* Trois APIs supports: blockscout pour evm,  moralis pour SVM et CMC pour les quotes
* Les charts sont pour le moment sur jupyter avec ipychart mais j'ai l'intention de faire une interface en vueJS + une API via fastAPI + graphQL
* tags via un fichier json
* Wallets custom(remplit à la main) via un fichier de configuration custom, je passerais peut etre au toml...

à Venir:
* Assistant forecast: Assistant calcul RR par token ou par categories de tokens
  * Pour un token le calcul sera classique
  * Pour un ensemble ce sera sur la base de pourcentage (prix actuel 100% on vise 120% et on craint 70%)
* API : dans l'idée de faire plus tard une appli web / mobile
* Une bdd: pour rendre l'appli multi-utilisateur et permettre le suivi detaillé des tokens
* Interface web : pour faire ses custom wallet et suivre plus facilement ses wallets
* Interface mobile: pourquoi pas?

## Fichiers de configurations:

### extra_positions.txt

C'est le fameux fichier de preparation des wallets customs. Il permet de generer des customs wallets et aussi un fichier d'exemple de tags.
Je n'ai pas l'intention pour le moment de gerer la fusions des fichiers tags. Ce n'est pas compliqué mais pas la priorité.

Le format actuel est le suivant :

```code
TAG1_TAG2:WALLET:BLOCKCHAIN:NOMDEX_TOKEN1_TOKEN2_TOKENX:NATIVE_BALANCE:USD_BALANCE:EXCHANGE_RATE
```

Comme vous le voyez le separateur de chaque section est le ":".
Certaines sections ont aussi un separateur :

* TAG1_TAG2 : On peut y mettre une multitude de TAGS separés par un "_"
* NOMDEX_TOKENX : lorqu'il n'y a qu'un element il s'agit d'un TOKEN mais s'il y a plus d'elements le premier representera toujours le DEX.
  * Le stacking n'a qu'un DEX + TOKEN ce qui donne LIDO_ETH. 
  * Le Farming / Liquidity Pool(LP) / Liquidity Pool Composed(LPC) peuvent en avoir une infinité mais le premier element est le DEX tel que BEEFY_FRAX_USDC_USDT.

Le reste n'a qu'un element ne pas porter attention aux "_" :-/

~~D'ou mon envie de faire du TOML...C'est pas compliqué aujourd'hui pour moi mais demain...Et pour un utilisateur tiers ça doit deja etre compliqué.~~
Reflexion faite le TOML n'est pas utile car il n'y a que les tags à parser. La concatenation des actifs DEX n'a pas à l'etre car je dois le differentier du reste.

### custom_wallets.json

fichier de sauvegarde:restauration des customs_wallets. L'idée est de les charger à par et eventuellement les fusionner avec les wallets chargé via API. La fusion est pris en charge.

### hf.json

L'historique des totaux scrapés.

### res_cmc.json

Contient le resultat de CMC

### tags.json

Contient la definition des tags

### ** config_suivi_unitaire.json **

Ficher de configuration principal. Il contient les clés privés des API utilisés, les clés publiques des wallets cibles, les urls des APIs et le nom et chemin des fichiers cités précedement. C'est un fichier indispensable au fonctionnement de l'appli, les autres peuvent etre regeneré ou ne sont pas indispensable.


# Document Technique

- [Document Technique](#document-technique)
  - [Obligations à taux fixes](#obligations-à-taux-fixes)
    - [Valeur de l'obligation](#valeur-de-lobligation)
    - [Sous-jacents (TO DO)](#sous-jacents-to-do)
    - [Risque d'une obligation](#risque-dune-obligation)
  - [Options Vanilles](#options-vanilles)
    - [Prix d'une option vanille (TO DO)](#prix-dune-option-vanille-to-do)
    - [Mesures de risque : les grecques](#mesures-de-risque--les-grecques)
  - [Produits à stratégie optionnelle](#produits-à-stratégie-optionnelle)
    - [Spreads](#spreads)
    - [Stratégies](#stratégies)
    - [Mesures de risque: les grecques](#mesures-de-risque-les-grecques)
  - [Options à barrière](#options-à-barrière)
  - [Options Binaires](#options-binaires)
    - [Touch Option](#touch-option)
    - [No Touch Option](#no-touch-option)
  - [Produits structurés](#produits-structurés)
    - [Reverse Convertible 1220](#reverse-convertible-1220)
    - [Certificat Outperformance 1310](#certificat-outperformance-1310)
    - [Mesures de risque](#mesures-de-risque)

## Obligations à taux fixes

### Valeur de l'obligation

Une obligation est un instrument à revenu fixe qui représente un morceau de dette émis par une entreprise, une collectivité territoriale ou un état. Les obligations sont utilisées par les émetteurs pour lever des capitaux.
En prêtant de l'argent, le détenteur de l'obligation reçoit des coupons de manière périodique ainsi que l'investissement initial à l'échéance de l'obligation.

Une obligation à coupon génère une série de flux financiers. Chaque flux est équivalent à une obligation zéro-coupon s'il est considéré indépendament des autres. Nous appliquons cette méthode pour le calcul de la valeur de notre obligation qui est alors égale à :
$$B = \frac{c}{m}\sum^N_{t=1}\exp(-\frac{r_{cont}(t)}{m}\times t) + F \times exp(-\frac{r_{cont}(N)}{m}\times N)$$
avec:

- \(m\): nombre de coupons par année ;
- \(c\): valeur du coupon annualisée ;
- \(r_{cont}(t)\): taux spot continu en date \(t\) ;
- \(N\): nombre de périodes avant maturité ;
- \(F\): valeur de l'obligation au moment de son émission.

### Sous-jacents (TO DO)

### Risque d'une obligation

Duration d'une obligation:
La duration d'une obligation est une mesure de sensibilité du prix de l'obligation aux variations des taux d'intérêts. Plus la duration est élevée, plus le risque de taux est grand.
$$D=\frac{\frac{c}{m}\sum^N_{t=1}\exp(-\frac{r_{YTM}}{m}\times t)\times t}{B}$$

Convexité d'une obligation:
La convexité est une mesure de la courbure de la relation entre le prix de l'obligation et la courbe des taux d'intérêts.
$$C=\frac{c}{m}\sum^N_{t=1}\exp(-\frac{r_{YTM}}{m}\times t)\times t^2$$

## Options Vanilles

*__Call :__*
Une option d'achat donne le droit à son détenteur d'acheter une certaine quantité d'un actif sous-jacent à une date future donnée et à un prix convenu en amont.

Un investisseur peuvent faire le choix d'avoir une position short (vendeuse) ou long (acheteuse) sur le call. Son payoff sera alors:

- Position Long : \(P=\max(S_t - K,0)\)
- Position Short : \(P=\min(K - S_t,0)\)

*__Put :__*
Une option de vente donne le droit à son détenteur de vendre une certaine quantité d'un actif sous-jacent à une date future donnée et à un prix convenu en amont.

Un investisseur peuvent faire le choix d'avoir une position short (vendeuse) ou long (acheteuse) sur le put. Son payoff sera alors:

- Position Long : \(P=\max(K - S_t,0)\)
- Position Short : \(P=\min(S_t - K,0)\)

### Prix d'une option vanille (TO DO)

### Mesures de risque : les grecques

Instruments de base de la gestion financière des options qui découlent du modèle de Black-Scholes & Merton. Ces indicateurs calculent l'impact sur le prix de l'option d'une variation des paramètres qui le forment :

- Delta: variations de prix du sous-jacent ;

\(\Delta_{call}=\mathcal{N}(d_1)\exp(-cT)\)
\(\Delta_{call}=(\mathcal{N}(d_1)-1)\exp(-cT)\)

- Gamma: sa convexité spot ;

\(\Gamma=\frac{\mathcal{N}'(d_1)\exp(-cT)}{S_0\sigma\sqrt{T}}\)

- Vega: la volatilité ;

\(\nu=S_0\sqrt{T}\mathcal{N}'(d_1)\exp(-cT)\)

- Theta: durée de vie de l'option ;

\(Theta_{call} = -\frac{S_0\exp(-cT)\mathcal{N}'(d_1)\sigma}{2\sqrt{T}}+qS_0\mathcal{N}(d_1)\exp(-cT)-rK\exp(-rT)\mathcal{N}(d_2)\)
\(Theta_{put} = -\frac{S_0\exp(-cT)\mathcal{N}'(d_1)\sigma}{2\sqrt{T}}-qS_0\mathcal{N}(d_1)\exp(-cT)+rK\exp(-rT)\mathcal{N}(d_2)\)

- Rho: variation du taux d'intérêt sans risque.

\(\rho_{call}=KT\exp(-rT)\mathcal{N}(d_2)\)
\(\rho_{put}=-KT\exp(-rT)\mathcal{N}(-d_2)\)

## Produits à stratégie optionnelle

Une stratégie optionnelle consiste à acheter ou vendre plusieurs options vanilles dans le but de bénéficier des mouvements anticipés de marché.

### Spreads

*__Call Spread :__*
Stratégie optionnelle qui se traduit par l’achat d’un call que l’on compense (en même temps) par la vente d’un call sur le même sous-jacent, de même maturité mais avec un strike supérieur. Le payoff d’un call spread est :
\(p = \max(K_1-S_T,0) - \max(K_2-S_T,0)\)

*__Put Spread :__*
Stratégie optionnelle qui se traduit par l’achat d’un put que l’on compense (en même temps) par la vente d’un put sur le même sous-jacent, de même maturité mais avec un strike supérieur. Le payoff d’un put spread est :
\(p = \max(K_2-S_T,0) - \max(K_1-S_T,0)\)

*__Butterfly Spread :__*
Stratégie optionnelle qui se traduit par la combinaison d’un call spread et d’un put spread. Le payoff d’un butterfly spread est :
\(p=\max(S_T-K_1,0)-2\times\max(S_T-K_2,0)+\max(S_T-K_3,0)\)

### Stratégies

*__Straddle :__*
Stratégie optionnelle qui consiste à acheter ou vendre un put et un call du même sous-jacent, de même date de maturité, et de même strike. Le payoff d’un straddle est :

- \(S_T \leq K : p = K-S_T\)
- \(S_T>K : p=S_T-K\)

*__Strangle :__*
Stratégie optionnelle qui consiste à acheter ou vendre un put et un call du même sous-jacent, de même date de maturité, mais de strike différent : le call doit avoir un strike supérieur au put. Le payoff d’un strangle est :

- \(S_T < K_1 : p=K_1-S_T\)
- \(K_1 \leq S_T \leq K_2 : p=0\)
- \(S_T > K_2 : p= S_T - K_2\)

*__Strip :__*
Stratégie optionnelle qui consiste à acheter deux puts et un call du même sous-jacent, de même date de maturité, et de même strike. Le payoff d’un strip est :

- \(S_T \leq K : p= 2\times(K-S_T)\)
- \(S_T>K : p= S_T-K\)

*__Strap :__*
Stratégie optionnelle qui consiste à acheter deux calls et un put du même sous-jacent, de même date de maturité, et de même strike. Le payoff d’un strap est :

- \(S_T<=K : p=K-S_T\)
- \( S_T>K : p=2\times(S_T-K)\)

### Mesures de risque: les grecques

Pour calculer les grecques associés aux différentes stratégies optionnelles, nous avons combiné les grecques des produits les composants.

## Options à barrière

*__Knock-Out :__*
Option à barrière qui expire si le prix du sous-jacent dépasse un certain niveau fixé préalablement. Si le spot dépasse la barrière alors le payoff de l'option est nul.

*__Knock-In :__*
Option à barrière qui commence à se comporter comme une option normale si le niveau de barrière prédéfini est franchi par le prix de l'actif sous-jacent.

## Options Binaires

Type d'option ayant deux issues possibles à l'échéance : si l'option termine dans la monnaie, le détenteur gagne le montant prévu, sinon il perd la totalité de la mise engagée.

*__Call Binaire :__*
Option qui verse une prime à son détenteur si le prix du sous-jacent augmente et devient supérieur ou égal au strike de l'option avant son expiration.

*__Put Binaire :__*
Option qui verse une prime à son détenteur si le prix du sous-jacent diminue et devient inférieur ou égal au strike de l'option avant son expiration.

### Touch Option

*__One Touch :__*
Option qui verse une prime à son détenteur si le prix du sous-jacent atteint le prix d'exercice (strike) avant l'expiration de l'option. Si le spot reste strictement inférieur au strike en tout temps alors le payoff de l'option est 0.

*__Double One Touch :__*
Option qui verse une prime à son détenteur si le prix du sous-jacent sort de la fourchette de prix déterminée à l'achat de l'option. Si le prix spot reste dans la fourchette de prix alors le payoff de l'option est nul.

### No Touch Option

*__No Touch :__*
Option qui verse une prime à son détenteur si le prix du sous-jacent reste inférieur au niveau de strike jusqu'à expiration. Si le prix spot est, à un moment, supérieur ou égal au strike, alors le payoff de l'option est nul.

*__Double No Touch :__*
Option qui verse une prime à son détenteur si le prix du sous-jacent reste dans une fourchette de prix jusqu'à l'expiration. Si le prix du sous-jacent sort de la fourchette alors le payoff de l'option sera nul.

## Produits structurés

### Reverse Convertible 1220

Produit structuré qui garantie à son détenteur de recevoir un coupon annuel fixe et, à maturité, un nominal de 100%. Ce produit est composé de :

- Achat d’une obligation ;
- Vente d’un put

### Certificat Outperformance 1310

Produit structuré qui donne le possibilité à son détenteur de bénéficier d’une participation supérieure à 100% dans la hausse d’un sous-jacent, tout en conservant une exposition de 100% à la baisse..

Ce produit est composé de :

- Achat d’un call de strike nul ;
- Achat d’un (niveau de participation - 1) call à la monnaie.

Le niveau de participation représente la vitesse à laquelle le payoff du produit augmente au-dessus du niveau du strike.

### Mesures de risque

Pour calculer les grecques associés aux différentes stratégies optionnelles, nous avons combiné les grecques des produits les composants.

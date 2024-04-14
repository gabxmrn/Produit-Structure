# Document Technique

- [Document Technique](#document-technique)
  - [Obligations à taux fixes](#obligations-à-taux-fixes)
    - [Valeur de l'obligation](#valeur-de-lobligation)
    - [Sous-jacents (TO DO)](#sous-jacents-to-do)
    - [Mesures de risque](#mesures-de-risque)
  - [Options Vanilles](#options-vanilles)
    - [Call](#call)
    - [Put](#put)
    - [Prix d'une option vanille (TO DO)](#prix-dune-option-vanille-to-do)
    - [Mesures de risque : les grecques](#mesures-de-risque--les-grecques)
  - [Produits à stratégie optionnelle](#produits-à-stratégie-optionnelle)
    - [Call Spread](#call-spread)
    - [Put Spread](#put-spread)
    - [Butterfly Spread](#butterfly-spread)
    - [Straddle](#straddle)
    - [Strangle](#strangle)
    - [Strip](#strip)
    - [Strap](#strap)
    - [Mesures de risque: les grecques](#mesures-de-risque-les-grecques)
  - [Options à barrière](#options-à-barrière)
  - [Options binaires](#options-binaires)
  - [Produits structurés](#produits-structurés)

## Obligations à taux fixes

### Valeur de l'obligation

Une obligation est un instrument à revenu fixe qui représente un morceau de dette émis par une entreprise, une collectivité territoriale ou un état. Les obligations sont utilisées par les émetteurs pour lever des capitaux.
En prêtant de l'argent, le détenteur de l'obligation reçoit des coupons de manière périodique ainsi que l'investissement initial à l'échéance de l'obligation.

Une obligation à coupon génère une série de flux financiers. Chaque flux est équivalent à une obligation zéro-coupon s'il est considéré indépendament des autres. Nous appliquons cette méthode pour le calcul de la valeur de notre obligation qui est alors égale à :
$$B = \frac{c}{m}\sum^N_{t=1}\exp(-\frac{r_{cont}(t)}{m}*t) + F * exp(-\frac{r_{cont}(N)}{m}*N)$$
avec:

- \(m\): nombre de coupons par année ;
- \(c\): valeur du coupon annualisée ;
- \(r_{cont}(t)\): taux spot continu en date \(t\) ;
- \(N\): nombre de périodes avant maturité ;
- \(F\): valeur de l'obligation au moment de son émission.

### Sous-jacents (TO DO)

### Mesures de risque

Duration d'une obligation:
La duration d'une obligation est une mesure de sensibilité du prix de l'obligation aux variations des taux d'intérêts. Plus la duration est élevée, plus le risque de taux est grand.
$$D=\frac{\frac{c}{m}\sum^N_{t=1}\exp(-\frac{r_{YTM}}{m}*t)*t}{B}$$

Convexité d'une obligation:
La convexité est une mesure de la courbure de la relation entre le prix de l'obligation et la courbe des taux d'intérêts.
$$C=\frac{c}{m}\sum^N_{t=1}\exp(-\frac{r_{YTM}}{m}*t)*t^2$$

## Options Vanilles

### Call

Une option d'achat donne le droit à son détenteur d'acheter une certaine quantité d'un actif sous-jacent à une date future donnée et à un prix convenu en amont.

Un investisseur peuvent faire le choix d'avoir une position short (vendeuse) ou long (acheteuse) sur le call. Son payoff sera alors:

- Position Long : \(P=\max(S_t - K,0)\)
- Position Short : \(P=\min(K - S_t,0)\)

### Put

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

\(\rho_{call}=KT\exp(_rT)\mathcal{N}(d_2)\)
\(\rho_{put}=-KT\exp(_rT)\mathcal{N}(-d_2)\)

## Produits à stratégie optionnelle

### Call Spread

### Put Spread

### Butterfly Spread

### Straddle

### Strangle

### Strip

### Strap

### Mesures de risque: les grecques

## Options à barrière

## Options binaires

## Produits structurés

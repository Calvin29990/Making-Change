# Méthodologie — prototype, à discuter

Pour une dette en devise étrangère et des flux disponibles (CFADS) en devise locale, le taux S est exprimé en unités locales par unité étrangère. Une dépréciation d signifie que la monnaie locale perd d de sa valeur en devise étrangère : S_choc = S / (1 - d). Pour une hausse donnée de S, d = 1 - S / S_choc. Cette convention évite de confondre une baisse de valeur de 20 % avec une hausse du taux de 20 % : cette dernière est ici de 25 %.

À chaque année t : principal remboursé = principal initial / durée ; intérêts = capital restant au début × taux annuel ; service en devise = principal + intérêts. Le taux stressé est supposé atteint immédiatement et constant ensuite. Sans couverture : service × S_choc. Avec couverture hypothétique h : service × [(1-h) × S_choc + h × taux couvert] + service × h × taux couvert × coût. Le taux couvert et le coût sont saisis par l'utilisateur. Le DSCR est CFADS annuel / service annuel en monnaie locale, avant et après couverture. CFADS positif ou nul, constant et sans indexation ; le coût est intégré au service couvert.

La comparaison des scénarios n'est pas une prédiction probabiliste : elle ne chiffre ni probabilité, ni valeur de marché, ni disponibilité réelle de forward, ni marges, collatéral, risque de contrepartie, contraintes de capital ou comptabilité de couverture. Aucune extrapolation automatique d'un cours ou d'une parité. Ce modèle est une simplification conçue pour discuter de mécanismes, pas un résultat présenté comme tiré directement d'un article.

## Questions de recherche ouvertes

- Cette interface sert-elle vraiment les PME et porteurs de projets ? Tester en entretien.
- Quel échéancier réel, quels revenus indexés, covenants et réserves faudrait-il prendre en compte ?
- Quelles données et couvertures sont accessibles pour chaque paire et chaque maturité ?
- La simulation peut-elle aider à discuter la bancabilité sans laisser croire à un effet causal démontré ?

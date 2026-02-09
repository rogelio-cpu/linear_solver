document.addEventListener('DOMContentLoaded', () => {
    const generateBtn = document.getElementById('generate-fields-btn');
    const dynamicInputs = document.getElementById('dynamic-inputs');
    const objFuncInputs = document.getElementById('objective-function-inputs');
    const constraintsInputs = document.getElementById('constraints-inputs');
    const solveBtn = document.getElementById('solve-btn');
    const resultsArea = document.getElementById('results-area');
    const resultsContent = document.getElementById('results-content');
    const simplexForm = document.getElementById('simplex-form');

    generateBtn.addEventListener('click', () => {
        const numVars = parseInt(document.getElementById('num-vars').value);
        const numConstraints = parseInt(document.getElementById('num-constraints').value);

        // Clear previous inputs
        objFuncInputs.innerHTML = '';
        constraintsInputs.innerHTML = '';

        // Generate Objective Function Inputs
        let objHtml = 'Z = ';
        for (let i = 0; i < numVars; i++) {
            objHtml += `<input type="number" step="any" class="coefficients-input obj-coeff" required> x<sub>${i + 1}</sub>`;
            if (i < numVars - 1) objHtml += ' + ';
        }
        objFuncInputs.innerHTML = objHtml;

        // Generate Constraints Inputs
        for (let i = 0; i < numConstraints; i++) {
            let rowHtml = `<div class="constraint-row">`;
            for (let j = 0; j < numVars; j++) {
                rowHtml += `<input type="number" step="any" class="coefficients-input constraint-coeff" data-row="${i}" data-col="${j}" required> x<sub>${j + 1}</sub>`;
                if (j < numVars - 1) rowHtml += ' + ';
            }

            rowHtml += `
                <select class="constraint-sign" data-row="${i}">
                    <option value="<=">&le;</option>
                    <option value=">=">&ge;</option>
                    <option value="=">=</option>
                </select>
                <input type="number" step="any" class="coefficients-input rhs-value" data-row="${i}" required>
            </div>`;
            constraintsInputs.innerHTML += rowHtml;
        }

        dynamicInputs.style.display = 'block';
    });

    simplexForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        console.log("Form submitted");

        const solveBtn = document.getElementById('solve-btn');
        const originalBtnText = solveBtn.textContent;
        solveBtn.textContent = 'Solving...';
        solveBtn.disabled = true;

        try {
            const numVars = parseInt(document.getElementById('num-vars').value);
            const numConstraints = parseInt(document.getElementById('num-constraints').value);
            const maximize = document.querySelector('input[name="maximize"]:checked').value === 'true';

            console.log(`Solving: Vars=${numVars}, Constraints=${numConstraints}, Maximize=${maximize}`);

            // Collect Objective Coefficients
            const objCoeffs = Array.from(document.querySelectorAll('.obj-coeff')).map(input => parseFloat(input.value));

            // Collect Constraints
            const constraintMatrix = [];
            const rhsValues = [];
            const constraintSigns = [];

            for (let i = 0; i < numConstraints; i++) {
                const row = [];
                for (let j = 0; j < numVars; j++) {
                    const val = document.querySelector(`.constraint-coeff[data-row="${i}"][data-col="${j}"]`).value;
                    row.push(parseFloat(val));
                }
                constraintMatrix.push(row);

                const sign = document.querySelector(`.constraint-sign[data-row="${i}"]`).value;
                constraintSigns.push(sign);

                const rhs = document.querySelector(`.rhs-value[data-row="${i}"]`).value;
                rhsValues.push(parseFloat(rhs));
            }

            const payload = {
                objective_coefficients: objCoeffs,
                constraint_matrix: constraintMatrix,
                rhs_values: rhsValues,
                constraint_signs: constraintSigns,
                maximize: maximize
            };

            console.log("Payload:", payload);

            const response = await fetch('/solve/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(payload)
            });

            console.log("Response status:", response.status);
            const data = await response.json();
            console.log("Response data:", data);

            if (response.ok) {
                displayResults(data);
            } else {
                console.error("Server Error:", data.error);
                resultsContent.innerHTML = `<div class="alert alert-danger" style="color: red; padding: 10px; border: 1px solid red; border-radius: 4px; background-color: #ffeeee;">Error: ${data.error}</div>`;
                resultsArea.style.display = 'block';
            }
        } catch (error) {
            console.error("JS Error:", error);
            resultsContent.innerHTML = `<div class="alert alert-danger" style="color: red; padding: 10px; border: 1px solid red; border-radius: 4px; background-color: #ffeeee;">Network/JS Error: ${error.message}</div>`;
            resultsArea.style.display = 'block';
        } finally {
            solveBtn.textContent = originalBtnText;
            solveBtn.disabled = false;
        }
    });

    function displayResults(data) {
        // Status translations
        const statusLabels = {
            'optimal': 'Optimal',
            'infeasible': 'Pas de solution',
            'unbounded': 'Non borné',
            'error': 'Erreur'
        };

        let html = '<div class="result-summary">';
        html += '<h4>✅ Solution Trouvée</h4>';
        html += `<p class="explanation">Le solveur a terminé l'analyse de votre problème de programmation linéaire.</p>`;
        html += `<p><strong>Statut:</strong> <span class="status-badge ${data.status}">${statusLabels[data.status] || data.status}</span></p>`;
        html += `<p><strong>Message:</strong> ${data.message || ''}</p>`;
        html += `<p><strong>Valeur de la Fonction Objectif (Z):</strong> <span class="highlight">${data.objective_value}</span></p>`;
        html += `<p class="explanation">C'est la valeur maximale (ou minimale) que votre fonction objectif peut atteindre tout en respectant les contraintes.</p>`;
        html += '<p><strong>Variables de Décision:</strong></p>';
        html += `<p class="explanation">Ces valeurs représentent les quantités optimales pour chaque variable de votre problème.</p>`;
        html += '<ul class="variable-list">';
        data.variables.forEach((val, idx) => {
            html += `<li>x<sub>${idx + 1}</sub> = <strong>${val}</strong></li>`;
        });
        html += '</ul>';
        html += '</div>';

        // Display Iterations (Step-by-Step)
        if (data.iterations && data.iterations.length > 0) {
            html += '<div class="iterations-section">';
            html += '<h4>📊 Étapes de Résolution Détaillées</h4>';
            html += `<p class="section-explanation">Voici le détail de chaque étape du processus de résolution par la méthode du Simplex. Chaque tableau montre l'état des calculs à une étape donnée.</p>`;

            data.iterations.forEach((iter, index) => {
                html += `<div class="iteration-block">`;

                // Phase explanation
                let phaseExplanation = '';
                if (iter.phase === 1) {
                    phaseExplanation = 'La Phase 1 cherche une solution de base initiale réalisable. Elle minimise les variables artificielles.';
                } else {
                    phaseExplanation = 'La Phase 2 optimise la fonction objectif à partir de la solution de base réalisable trouvée.';
                }

                if (iter.iter === undefined) {
                    html += `<h5>Phase ${iter.phase} - Tableau Initial</h5>`;
                    html += `<p class="phase-explanation">${phaseExplanation}</p>`;
                    html += `<p class="step-explanation">Ceci est le tableau de départ avant toute itération. La dernière ligne contient les <strong>coûts réduits</strong> (indicateurs d'optimalité).</p>`;
                } else {
                    html += `<h5>Phase ${iter.phase} - Itération ${iter.iter}</h5>`;
                    html += `<p class="phase-explanation">${phaseExplanation}</p>`;
                }

                if (iter.entering !== undefined) {
                    html += `<div class="pivot-info">`;
                    html += `<p><strong>🔄 Opération de Pivot:</strong></p>`;
                    html += `<ul>`;
                    html += `<li><strong>Variable entrante:</strong> x<sub>${iter.entering + 1}</sub> (colonne ${iter.entering + 1})</li>`;
                    html += `<li><strong>Variable sortante:</strong> Ligne ${iter.leaving_row + 1}</li>`;
                    html += `</ul>`;
                    html += `<p class="step-explanation">La variable entrante est celle qui améliorera le plus la fonction objectif. La ligne sortante est déterminée par le <strong>test du ratio minimum</strong> (valeur RHS ÷ coefficient positif de la colonne pivot).</p>`;
                    html += `</div>`;
                }

                // Render Tableau as HTML Table
                if (iter.tableau) {
                    html += '<div class="tableau-container">';
                    html += `<p class="tableau-title"><strong>Tableau Simplex:</strong></p>`;
                    html += '<table class="simplex-tableau">';

                    // Header row
                    html += '<thead><tr>';
                    html += '<th>Base</th>';
                    const numCols = iter.tableau[0].length;
                    for (let j = 0; j < numCols - 1; j++) {
                        html += `<th>x<sub>${j + 1}</sub></th>`;
                    }
                    html += '<th>RHS (b)</th></tr></thead>';

                    // Body rows
                    html += '<tbody>';
                    iter.tableau.forEach((row, rowIdx) => {
                        const isObjectiveRow = rowIdx === iter.tableau.length - 1;
                        const rowLabel = isObjectiveRow ? 'Z (Coûts réduits)' : `Contrainte ${rowIdx + 1}`;
                        html += `<tr class="${isObjectiveRow ? 'objective-row' : ''}">`;
                        html += `<td class="row-label">${rowLabel}</td>`;
                        row.forEach((cell, colIdx) => {
                            const cellValue = typeof cell === 'number' ? cell.toFixed(4) : cell;
                            html += `<td>${cellValue}</td>`;
                        });
                        html += '</tr>';
                    });
                    html += '</tbody></table>';
                    html += `<p class="tableau-legend">💡 <em>La dernière ligne (en jaune) contient les coûts réduits. Si tous sont ≥ 0, la solution est optimale.</em></p>`;
                    html += '</div>';
                }

                html += `<p class="iteration-obj">📈 Valeur Objectif à cette étape: <strong>${iter.obj !== undefined ? iter.obj.toFixed(4) : 'N/A'}</strong></p>`;
                html += '</div>';
            });

            html += `<div class="final-note">`;
            html += `<p>✅ <strong>Fin du processus:</strong> Tous les coûts réduits sont non-négatifs (≥ 0), ce qui signifie que la solution optimale a été atteinte.</p>`;
            html += `</div>`;
            html += '</div>';
        }

        resultsContent.innerHTML = html;
        resultsArea.style.display = 'block';
    }
});

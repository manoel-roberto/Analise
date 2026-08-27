/**
 * =========================================================================
 * CONFIGURAÇÃO DAS COLUNAS
 * =========================================================================
 * Tabela de conversão de Letra para Número:
 * H=8 | L=12 | O=15 | P=16 | Q=17 | S=19 | T=20 | X=24 | Y=25
 * =========================================================================
 */
var COL_CARGO         = 8;  // Coluna H (Cargo / Função)
var COL_GRUPO         = 12; // Coluna L (Grupos)
var COL_VALOR_SIMBOLO = 15; // Coluna O (Valor do Símbolo)
var COL_VENC_BASICO   = 16; // Coluna P (Vencimento Básico)
var COL_DAS_DAI       = 17; // Coluna Q (DAS ou DAI - Opção do Servidor)
var COL_PERC_ATUAL    = 20; // Coluna T (% RTI Atual)

// Colunas de destino:
var COL_NOVO_PERC     = 24; // Coluna X (Novo % RTI)
var COL_NOVO_VALOR    = 25; // Coluna Y (Novo Valor R$)

/**
 * Cria o menu personalizado quando a planilha é aberta
 */
function onOpen() {
  var ui = SpreadsheetApp.getUi();
  ui.createMenu('⚙️ Simulação RTI')
      .addItem('Configurar Acréscimos Múltiplos', 'abrirPainelRTI')
      .addToUi();
}

/**
 * Funções auxiliares de conversão e limpeza
 */
function parseCurrency(val) {
  if (val === null || val === undefined || val === '') return 0;
  if (typeof val === 'number') return isNaN(val) ? 0 : val;
  var str = val.toString().replace('R$', '').trim();
  if (str === '') return 0;
  if (str.indexOf(',') !== -1) {
    str = str.replace(/\./g, '').replace(',', '.');
  }
  var parsed = parseFloat(str);
  return isNaN(parsed) ? 0 : parsed;
}

function parsePercent(val) {
  if (val === null || val === undefined || val === '') return 0;
  if (typeof val === 'number') return isNaN(val) ? 0 : val;
  var str = val.toString().replace('%', '').trim();
  if (str === '') return 0;
  if (str.indexOf(',') !== -1) {
    str = str.replace(',', '.');
  }
  var parsed = parseFloat(str);
  if (isNaN(parsed)) return 0;
  return parsed / 100;
}

/**
 * Calcula a Base de Cálculo (BC) do RTI:
 * - Exceção: Se Coluna H (Cargo) for "Técnico Específico" => BC = Coluna O (Valor do Símbolo)
 * - Cenário 1: Se Coluna Q (DAS/DAI) == Coluna O (Valor Símbolo) => BC = Coluna Q
 * - Cenário 2: Se Coluna Q (DAS/DAI) != Coluna O (Valor Símbolo) => BC = Coluna P (Vencimento Básico)
 */
function obterBaseCalculo(cargo, valorSimbolo, vencBasico, dasDai) {
  var cargoStr = cargo ? cargo.toString().trim().toLowerCase() : '';
  if (cargoStr === 'técnico específico' || cargoStr === 'tecnico especifico') {
    return valorSimbolo;
  }
  return (Math.abs(dasDai - valorSimbolo) < 0.01) ? dasDai : vencBasico;
}

/**
 * Abre uma janela HTML estilizada para preencher os percentuais de acréscimo dos grupos.
 */
function abrirPainelRTI() {
  var htmlStr = `
    <!DOCTYPE html>
    <html>
    <head>
      <base target="_top">
      <style>
        body { font-family: Arial, sans-serif; padding: 10px; color: #333; }
        .linha { margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; }
        label { font-size: 14px; flex: 1; }
        input[type="number"] { width: 70px; padding: 5px; text-align: center; border: 1px solid #ccc; border-radius: 4px; }
        .botoes { margin-top: 20px; text-align: right; }
        button { padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; }
        .btn-salvar { background-color: #0F9D58; color: white; margin-left: 10px; font-weight: bold;}
        .btn-cancelar { background-color: #f1f3f4; color: #333; }
        .header-info { font-size: 12px; color: #666; margin-bottom: 15px; border-bottom: 1px solid #eee; padding-bottom: 10px;}
      </style>
    </head>
    <body>
      <div class="header-info">Digite o percentual de acréscimo para cada grupo (Ex: 5). Deixe 0 para apenas copiar o RTI atual sem aumento.</div>
      
      <div class="linha"><label>1. Acadêmicos (Diretor):</label><input type="number" id="g1" value="0" step="any"> %</div>
      <div class="linha"><label>2. ADM (Gestor Acadêmico):</label><input type="number" id="g2" value="0" step="any"> %</div>
      <div class="linha"><label>3. ADM (Gestor ADM):</label><input type="number" id="g3" value="0" step="any"> %</div>
      <div class="linha"><label>4. Assessor em ascensão:</label><input type="number" id="g4" value="0" step="any"> %</div>
      <div class="linha"><label>5. Assessores:</label><input type="number" id="g5" value="0" step="any"> %</div>
      <div class="linha"><label>6. Funções Comissionadas:</label><input type="number" id="g6" value="0" step="any"> %</div>
      
      <div class="botoes">
        <button class="btn-cancelar" onclick="google.script.host.close()">Cancelar</button>
        <button class="btn-salvar" id="btnSalvar" onclick="enviarDados()">Aplicar Simulação</button>
      </div>

      <script>
        function enviarDados() {
          document.getElementById('btnSalvar').innerText = 'Processando...';
          document.getElementById('btnSalvar').disabled = true;
          
          var dados = {
            '1.': document.getElementById('g1').value,
            '2.': document.getElementById('g2').value,
            '3.': document.getElementById('g3').value,
            '4.': document.getElementById('g4').value,
            '5.': document.getElementById('g5').value,
            '6.': document.getElementById('g6').value
          };
          
          google.script.run
            .withSuccessHandler(function(mensagem) {
              google.script.host.close();
            })
            .processarAcrescimosLote(dados);
        }
      </script>
    </body>
    </html>
  `;
  
  var htmlOutput = HtmlService.createHtmlOutput(htmlStr)
      .setWidth(450)
      .setHeight(400);
      
  SpreadsheetApp.getUi().showModalDialog(htmlOutput, 'Configurar Acréscimos RTI');
}

/**
 * Recebe os dados do painel HTML e processa os cálculos em lote.
 * Regra da Base de Cálculo (BC):
 * - Exceção: Se Coluna H (Cargo) for "Técnico Específico" => BC = Coluna O (Valor do Símbolo)
 * - Cenário 1: Se Coluna Q (DAS/DAI) == Coluna O (Valor Símbolo) => BC = Coluna Q
 * - Cenário 2: Se Coluna Q (DAS/DAI) != Coluna O (Valor Símbolo) => BC = Coluna P (Vencimento Básico)
 */
function processarAcrescimosLote(dadosAumento) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  var lastRow = sheet.getLastRow();
  if (lastRow < 2) return;
  
  var maxCol = Math.max(COL_NOVO_PERC, COL_NOVO_VALOR, COL_GRUPO, COL_DAS_DAI, COL_PERC_ATUAL, COL_VALOR_SIMBOLO, COL_VENC_BASICO, COL_CARGO);
  var dataRange = sheet.getRange(2, 1, lastRow - 1, maxCol); 
  var data = dataRange.getValues();
  
  var outPerc = [];
  var outValor = [];
  var contadorAlterados = 0;
  
  for (var i = 0; i < data.length; i++) {
    var rowData = data[i];
    
    var cargoAtual = rowData[COL_CARGO - 1] ? rowData[COL_CARGO - 1].toString().trim() : '';
    var grupoAtual = rowData[COL_GRUPO - 1] ? rowData[COL_GRUPO - 1].toString().trim() : '';
    var percAtual = parsePercent(rowData[COL_PERC_ATUAL - 1]); 
    var valorSimbolo = parseCurrency(rowData[COL_VALOR_SIMBOLO - 1]);
    var vencBasico = parseCurrency(rowData[COL_VENC_BASICO - 1]);
    var dasDai = parseCurrency(rowData[COL_DAS_DAI - 1]);
    
    // Definição dinâmica da Base de Cálculo (BC) com exceção para "Técnico Específico"
    var bc = obterBaseCalculo(cargoAtual, valorSimbolo, vencBasico, dasDai);
    
    // Identifica o acréscimo específico para o grupo lendo a configuração do painel
    var acrescimo = 0;
    if (grupoAtual.indexOf("1.") === 0) acrescimo = parseFloat(dadosAumento['1.']) / 100 || 0;
    else if (grupoAtual.indexOf("2.") === 0) acrescimo = parseFloat(dadosAumento['2.']) / 100 || 0;
    else if (grupoAtual.indexOf("3.") === 0) acrescimo = parseFloat(dadosAumento['3.']) / 100 || 0;
    else if (grupoAtual.indexOf("4.") === 0) acrescimo = parseFloat(dadosAumento['4.']) / 100 || 0;
    else if (grupoAtual.indexOf("5.") === 0) acrescimo = parseFloat(dadosAumento['5.']) / 100 || 0;
    else if (grupoAtual.indexOf("6.") === 0) acrescimo = parseFloat(dadosAumento['6.']) / 100 || 0;
    
    // Novo Percentual = Percentual Anterior (T) + Acréscimo
    var novoPerc = percAtual + acrescimo;
    if (acrescimo !== 0) {
      contadorAlterados++;
    }
    
    // Novo Valor R$ (Y) = Novo Percentual (X) * Base de Cálculo
    var novoValor = bc * novoPerc;
    
    outPerc.push([novoPerc]);
    outValor.push([novoValor]);
  }
  
  // Salva na planilha
  sheet.getRange(2, COL_NOVO_PERC, outPerc.length, 1).setValues(outPerc).setNumberFormat('0.00%');
  sheet.getRange(2, COL_NOVO_VALOR, outValor.length, 1).setValues(outValor).setNumberFormat('"R$" #,##0.00');
  
  SpreadsheetApp.getUi().alert('Simulação Concluída!\n\nRegistros que sofreram acréscimo: ' + contadorAlterados);
  return "OK";
}

/**
 * Gatilho Inteligente (onEdit): Calcula automaticamente ao editar as células manualmente.
 * Automação bilateral com base dinâmica e prevenção de divisão por zero.
 */
function onEdit(e) {
  if (!e || !e.range) return;
  var sheet = e.range.getSheet();
  
  var row = e.range.getRow();
  var col = e.range.getColumn();
  
  if (row < 2 || e.range.getNumRows() > 1 || e.range.getNumColumns() > 1) return;
  
  if (col === COL_NOVO_PERC || col === COL_NOVO_VALOR) {
    var cargo = sheet.getRange(row, COL_CARGO).getValue();
    var valorSimbolo = parseCurrency(sheet.getRange(row, COL_VALOR_SIMBOLO).getValue()); 
    var vencBasico = parseCurrency(sheet.getRange(row, COL_VENC_BASICO).getValue()); 
    var dasDai = parseCurrency(sheet.getRange(row, COL_DAS_DAI).getValue());
    
    // Definição dinâmica da Base de Cálculo (BC) com exceção para "Técnico Específico"
    var bc = obterBaseCalculo(cargo, valorSimbolo, vencBasico, dasDai);
    
    // Trata divisão por zero ou Base de Cálculo nula
    if (!bc || bc === 0 || isNaN(bc)) return; 
    
    if (col === COL_NOVO_PERC) {
      var percRaw = sheet.getRange(row, COL_NOVO_PERC).getValue();
      if (percRaw === '' || percRaw === null) return;
      var perc = parsePercent(percRaw);
      var novoValor = bc * perc; 
      sheet.getRange(row, COL_NOVO_VALOR).setValue(novoValor).setNumberFormat('"R$" #,##0.00');
    }
    
    if (col === COL_NOVO_VALOR) {
      var valorRaw = sheet.getRange(row, COL_NOVO_VALOR).getValue();
      if (valorRaw === '' || valorRaw === null) return;
      var valor = parseCurrency(valorRaw);
      var novoPerc = valor / bc; 
      sheet.getRange(row, COL_NOVO_PERC).setValue(novoPerc).setNumberFormat('0.00%');
    }
  }
}
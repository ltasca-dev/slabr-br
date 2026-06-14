const ngrok = require("ngrok");

(async function() {
  try {
    const url = await ngrok.connect(5000);
    console.log(`URL PUBLICA: ${url}`);
    console.log("SLABR está exposto em:", url);
    console.log("Acesse: " + url + "/home-public");
    console.log("");
    console.log("Tunnel ativo. Pressione Ctrl+C para parar.");
  } catch (err) {
    console.log("Erro:", err);
  }
})();

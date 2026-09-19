/* =====================================================================
   Sensoria — shared front-end logic (homepage + every product page)
   Cart persists via localStorage so it survives navigation between pages.
   All product content is pre-rendered as static HTML by generate.py —
   this file only wires up interactions via data-* attributes.
===================================================================== */
const WHATSAPP_NUMBER = "221781537491";
const CART_KEY = "sensoria_cart_v1";

/* Product pages live one level deep (/produits/xxx.html). Cart items store
   "canonical" root-relative image paths (e.g. "assets/x.png"); this prefix
   is applied only when DISPLAYING them, so the cart works the same
   regardless of which page it is opened from. */
const ASSET_BASE = /\/(produits|collections)\//.test(location.pathname) ? "../" : "";

function fmt(n){ return Number(n).toLocaleString("fr-FR").replace(/,/g," "); }

/* ===================== CART STORE ===================== */
function loadCart(){
  try { return JSON.parse(localStorage.getItem(CART_KEY)) || []; }
  catch(e){ return []; }
}
function saveCart(cart){
  try { localStorage.setItem(CART_KEY, JSON.stringify(cart)); } catch(e){}
}

function addToCart(item){
  const cart = loadCart();
  cart.push(item);
  saveCart(cart);
  renderCart();
  openCart();
  pulseBadge();
}

function removeFromCart(idx){
  const cart = loadCart();
  cart.splice(idx,1);
  saveCart(cart);
  renderCart();
}

function pulseBadge(){
  const b = document.getElementById("cartBadge");
  if(!b) return;
  b.style.transform = "scale(1.4)";
  setTimeout(()=> b.style.transform = "scale(1)", 200);
}

function renderCart(){
  const itemsEl = document.getElementById("cartItems");
  const totalEl = document.getElementById("cartTotal");
  const badge = document.getElementById("cartBadge");
  const checkout = document.getElementById("cartCheckout");
  if(!itemsEl) return;

  const cart = loadCart();
  if(badge) badge.textContent = cart.length;

  if(cart.length === 0){
    itemsEl.innerHTML = `<p class="cart-empty">Votre sélection est vide.<br>Ajoutez des produits pour commander en une fois.</p>`;
  } else {
    itemsEl.innerHTML = cart.map((it, i) => `
      <div class="cart-item">
        <img src="${ASSET_BASE}${it.img}" alt="${it.name}">
        <div class="cart-item-info">
          <h5>${it.name}</h5>
          <span>${it.priceLabel || fmt(it.price) + " F CFA"}</span>
          <div class="cart-item-remove" data-remove="${i}">Retirer</div>
        </div>
      </div>
    `).join("");
    itemsEl.querySelectorAll("[data-remove]").forEach(btn=>{
      btn.addEventListener("click", ()=> removeFromCart(parseInt(btn.dataset.remove)));
    });
  }

  const total = cart.reduce((s,it)=> s + (Number(it.price) || 0), 0);
  if(totalEl) totalEl.textContent = fmt(total) + " F CFA";

  if(checkout){
    const lines = cart.map(it => `• ${it.name} — ${it.priceLabel || fmt(it.price) + " F CFA"}`).join("\n");
    const msg = cart.length
      ? `Bonjour Sensoria 🌸 Je souhaite commander :\n\n${lines}\n\nTotal estimé : ${fmt(total)} F CFA\n\nMerci de me confirmer la disponibilité et les modalités de livraison.`
      : `Bonjour Sensoria 🌸 je souhaite avoir des renseignements sur votre collection.`;
    checkout.href = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(msg)}`;
  }
}

function openCart(){
  document.getElementById("cartPanel")?.classList.add("open");
  document.getElementById("cartOverlay")?.classList.add("open");
}
function closeCart(){
  document.getElementById("cartPanel")?.classList.remove("open");
  document.getElementById("cartOverlay")?.classList.remove("open");
}

function orderSingle(item){
  const msg = `Bonjour Sensoria 🌸 Je souhaite commander :\n\n• ${item.name} — ${item.priceLabel || fmt(item.price) + " F CFA"}\n\nMerci de me confirmer la disponibilité et les modalités de livraison.`;
  window.open(`https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(msg)}`, "_blank");
}

/* ===================== GENERIC DELEGATED ACTIONS ===================== */
document.addEventListener("click", (e) => {
  const addBtn = e.target.closest("[data-add-cart]");
  if(addBtn){
    addToCart({
      name: addBtn.dataset.name,
      price: addBtn.dataset.price || 0,
      priceLabel: addBtn.dataset.priceLabel || "",
      img: addBtn.dataset.img
    });
    return;
  }

  const orderBtn = e.target.closest("[data-order]");
  if(orderBtn){
    orderSingle({
      name: orderBtn.dataset.name,
      price: orderBtn.dataset.price || 0,
      priceLabel: orderBtn.dataset.priceLabel || ""
    });
    return;
  }

  const infoBtn = e.target.closest("[data-order-info]");
  if(infoBtn){
    const msg = `Bonjour Sensoria 🌸 Je souhaite avoir des informations et le prix pour :\n\n• ${infoBtn.dataset.name}\n\nMerci de me confirmer la disponibilité.`;
    window.open(`https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(msg)}`, "_blank");
    return;
  }

  // wishlist heart on grid cards
  const wishBtn = e.target.closest("[data-wish]");
  if(wishBtn){
    wishBtn.classList.add("active");
    addToCart({
      name: wishBtn.dataset.name,
      price: wishBtn.dataset.price || 0,
      priceLabel: wishBtn.dataset.priceLabel || "",
      img: wishBtn.dataset.img
    });
    return;
  }

  // variant option (diffuser color / gel scent)
  const opt = e.target.closest(".variant-group [data-value]");
  if(opt){
    const group = opt.closest(".variant-group");
    group.querySelectorAll("[data-value]").forEach(b => b.classList.remove("active"));
    opt.classList.add("active");
    group.dataset.chosen = opt.dataset.value;
    group.dataset.chosenImg = opt.dataset.img;
    group.dataset.chosenImgCanonical = opt.dataset.imgCanonical || opt.dataset.img;
    const targetSel = group.dataset.targetImg;
    if(targetSel){
      const targetImg = document.querySelector(targetSel);
      if(targetImg){
        targetImg.style.opacity = 0;
        setTimeout(()=>{ targetImg.src = opt.dataset.img; targetImg.style.opacity = 1; }, 120);
      }
    }
    const labelSel = group.dataset.labelTarget;
    if(labelSel){
      const labelEl = document.querySelector(labelSel);
      if(labelEl) labelEl.textContent = opt.dataset.value;
    }
    return;
  }

  // add-to-cart for variant products
  const varAdd = e.target.closest("[data-add-cart-variant]");
  if(varAdd){
    const group = document.querySelector(varAdd.dataset.variantGroup || ".variant-group");
    if(!group) return;
    const chosen = group.dataset.chosen || group.querySelector("[data-value]")?.dataset.value;
    const img = group.dataset.chosenImgCanonical || group.querySelector("[data-value]")?.dataset.imgCanonical;
    addToCart({
      name: `${group.dataset.baseName} — ${chosen}`,
      price: group.dataset.basePrice,
      img
    });
    return;
  }

  const varOrder = e.target.closest("[data-order-variant]");
  if(varOrder){
    const group = document.querySelector(varOrder.dataset.variantGroup || ".variant-group");
    if(!group) return;
    const chosen = group.dataset.chosen || group.querySelector("[data-value]")?.dataset.value;
    orderSingle({ name: `${group.dataset.baseName} — ${chosen}`, price: group.dataset.basePrice });
    return;
  }
});

/* ===================== INIT ===================== */
document.addEventListener("DOMContentLoaded", () => {
  renderCart();
  initScrollReveal();
  initNav();
  initQuiz();
});

/* ===================== NAV / MOBILE MENU / CART TOGGLE ===================== */
function initNav(){
  const hamburger = document.getElementById("hamburger");
  const nav = document.getElementById("mainNav");
  if(hamburger && nav){
    hamburger.addEventListener("click", ()=> nav.classList.toggle("open"));
    nav.querySelectorAll("a").forEach(a => a.addEventListener("click", ()=> nav.classList.remove("open")));
  }
  document.getElementById("cartToggle")?.addEventListener("click", openCart);
  document.getElementById("cartClose")?.addEventListener("click", closeCart);
  document.getElementById("cartOverlay")?.addEventListener("click", closeCart);
}

/* ===================== SCROLL REVEAL ===================== */
function initScrollReveal(){
  const els = document.querySelectorAll(".reveal");
  if(!els.length) return;
  const obs = new IntersectionObserver((entries)=>{
    entries.forEach(e=>{
      if(e.isIntersecting){ e.target.classList.add("in"); obs.unobserve(e.target); }
    });
  }, { threshold:0.12 });
  els.forEach(el => obs.observe(el));
}

/* ===================== QUIZ (homepage only) ===================== */
function initQuiz(){
  const card = document.getElementById("quizCard");
  if(!card) return;
  const dataEl = document.getElementById("quizData");
  if(!dataEl) return;
  const PARFUMS = JSON.parse(dataEl.textContent);

  const steps = card.querySelectorAll(".quiz-step");
  const resultStep = card.querySelector('[data-step="result"]');
  const progressBar = document.getElementById("quizProgressBar");
  let scores = {};
  let currentStep = 0;

  function resetQuiz(){
    scores = {};
    PARFUMS.forEach(p => scores[p.key] = 0);
    currentStep = 0;
    steps.forEach((s,i)=> s.hidden = i !== 0);
    resultStep.hidden = true;
    progressBar.style.width = "0%";
  }
  resetQuiz();

  steps.forEach((step) => {
    step.querySelectorAll("button").forEach(btn=>{
      btn.addEventListener("click", () => {
        const tags = btn.dataset.tags.split(",");
        tags.forEach(t => scores[t] = (scores[t]||0) + 1);
        step.hidden = true;
        currentStep++;
        progressBar.style.width = Math.min(currentStep/3*100, 100) + "%";
        if(steps[currentStep]){
          steps[currentStep].hidden = false;
        } else {
          showQuizResult();
        }
      });
    });
  });

  function showQuizResult(){
    let bestKey = PARFUMS[0].key, bestScore = -1;
    Object.entries(scores).forEach(([k,v])=>{
      if(v > bestScore){ bestScore = v; bestKey = k; }
    });
    const p = PARFUMS.find(x => x.key === bestKey) || PARFUMS[0];
    document.getElementById("quizResultImg").src = p.img;
    document.getElementById("quizResultImg").alt = p.name;
    document.getElementById("quizResultName").textContent = `${p.name} — ${p.family}`;
    document.getElementById("quizResultDesc").textContent = p.desc;
    document.getElementById("quizResultLink").href = p.url;

    const addBtn = document.getElementById("quizAddCart");
    addBtn.onclick = () => addToCart({ name:`${p.name} — Eau de Parfum 50 ml`, price:p.price, img:p.img });

    resultStep.hidden = false;
  }

  document.getElementById("quizRestart").addEventListener("click", resetQuiz);
}

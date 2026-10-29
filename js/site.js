const QUOTE_EMAIL = "countryroadscleaningsolutions@gmail.com";

(() => {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  if ($("copyright-year")) $("copyright-year").textContent = String(new Date().getFullYear());

  const carousel = $("review-carousel");
  if (carousel) {
    const slides = [...document.querySelectorAll(".review-slide")];
    let reviewIndex = 0;
    let timer = null;
    let paused = reducedMotion.matches;
    let expanded = false;
    const stop = () => { if (timer) clearInterval(timer); timer = null; };
    const start = () => {
      stop();
      if (!paused && !expanded && !document.hidden && !carousel.matches(":hover") && !carousel.contains(document.activeElement)) {
        timer = setInterval(() => showReview(reviewIndex + 1), 7000);
      }
    };
    const updatePause = () => {
      $("review-pause").innerHTML = paused
        ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m8 4 12 8-12 8z"/></svg>'
        : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 5v14M15 5v14"/></svg>';
      $("review-pause").setAttribute("aria-label", paused ? "Play automatic reviews" : "Pause automatic reviews");
    };
    const showReview = (index, manual = false) => {
      reviewIndex = (index + slides.length) % slides.length;
      slides.forEach((slide, i) => { slide.hidden = i !== reviewIndex; });
      expanded = false;
      carousel.classList.remove("expanded");
      $("review-expand").textContent = "Read full review";
      $("review-expand").setAttribute("aria-expanded", "false");
      const current = slides[reviewIndex];
      $("review-name").textContent = current.dataset.name;
      const source = $("review-source");
      if (source) source.textContent = current.dataset.source || "Customer review";
      $("review-count").textContent = `${reviewIndex + 1} / ${slides.length}`;
      requestAnimationFrame(() => {
        const text = current.querySelector(".review-body");
        $("review-expand").hidden = text.scrollHeight <= text.clientHeight + 2;
      });
      if (manual) {
        $("review-announcement").textContent = `Review ${reviewIndex + 1} of ${slides.length}, from ${current.dataset.name}.`;
        start();
      }
    };
    $("review-prev").addEventListener("click", () => showReview(reviewIndex - 1, true));
    $("review-next").addEventListener("click", () => showReview(reviewIndex + 1, true));
    $("review-pause").addEventListener("click", () => { paused = !paused; updatePause(); start(); });
    $("review-expand").addEventListener("click", () => {
      expanded = !expanded;
      carousel.classList.toggle("expanded", expanded);
      $("review-expand").textContent = expanded ? "Show less" : "Read full review";
      $("review-expand").setAttribute("aria-expanded", String(expanded));
      start();
    });
    carousel.addEventListener("mouseenter", stop);
    carousel.addEventListener("mouseleave", start);
    carousel.addEventListener("focusin", stop);
    carousel.addEventListener("focusout", () => requestAnimationFrame(start));
    carousel.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        showReview(reviewIndex + (event.key === "ArrowLeft" ? -1 : 1), true);
      }
    });
    let touchX = null;
    let touchY = null;
    carousel.addEventListener("touchstart", (event) => {
      touchX = event.touches[0].clientX;
      touchY = event.touches[0].clientY;
      stop();
    }, { passive: true });
    carousel.addEventListener("touchend", (event) => {
      if (touchX !== null && event.changedTouches.length) {
        const dx = event.changedTouches[0].clientX - touchX;
        const dy = event.changedTouches[0].clientY - touchY;
        if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) showReview(reviewIndex + (dx < 0 ? 1 : -1), true);
      }
      touchX = null;
      touchY = null;
      start();
    }, { passive: true });
    document.addEventListener("visibilitychange", start);
    reducedMotion.addEventListener("change", (event) => {
      if (event.matches) { paused = true; updatePause(); }
      start();
    });
    window.addEventListener("resize", () => { if (!expanded) showReview(reviewIndex); });
    showReview(0);
    updatePause();
    start();
  }

  const photoButtons = [...document.querySelectorAll(".photo-button")];
  const photoDialog = $("photo-dialog");
  if (photoButtons.length && photoDialog) {
    let photoIndex = 0;
    const showPhoto = (index) => {
      photoIndex = (index + photoButtons.length) % photoButtons.length;
      const image = photoButtons[photoIndex].querySelector("img");
      $("lightbox-image").src = image.currentSrc || image.src;
      $("lightbox-image").alt = image.alt;
      const caption = photoButtons[photoIndex].parentElement.querySelector("figcaption");
      const label = caption ? caption.textContent.trim().replace(/^\d+\s*/, "") : "";
      $("lightbox-caption").textContent = `${photoIndex + 1} / ${photoButtons.length} · ${label}`;
    };
    photoButtons.forEach((button, index) => button.addEventListener("click", () => {
      showPhoto(index);
      photoDialog.showModal();
      document.body.style.overflow = "hidden";
    }));
    $("photo-prev").addEventListener("click", () => showPhoto(photoIndex - 1));
    $("photo-next").addEventListener("click", () => showPhoto(photoIndex + 1));
    photoDialog.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        showPhoto(photoIndex + (event.key === "ArrowLeft" ? -1 : 1));
      }
    });
  }

  const openDialog = (dialog) => { dialog.showModal(); document.body.style.overflow = "hidden"; };
  if ($("privacy-open")) $("privacy-open").addEventListener("click", () => openDialog($("privacy-dialog")));
  document.querySelectorAll("[data-close]").forEach((button) => {
    button.addEventListener("click", () => $(button.dataset.close).close());
  });
  document.querySelectorAll("dialog").forEach((dialog) => {
    dialog.addEventListener("close", () => { document.body.style.overflow = ""; });
    dialog.addEventListener("click", (event) => {
      const rect = dialog.getBoundingClientRect();
      const outside = event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom;
      if (event.target === dialog && outside) dialog.close();
    });
  });

  const mobileCta = $("mobile-cta");
  const heroCta = $("hero-cta");
  const quote = $("quote");
  const onQuotePage = /\/quote\/?$/.test(location.pathname);
  if (mobileCta && onQuotePage) mobileCta.classList.remove("visible");
  if (mobileCta && heroCta && quote && !onQuotePage && "IntersectionObserver" in window) {
    let heroPassed = false;
    let quoteVisible = false;
    const syncMobile = () => {
      mobileCta.classList.toggle("visible", heroPassed && !quoteVisible && !location.search.includes("quote=sent"));
    };
    new IntersectionObserver((entries) => {
      heroPassed = entries[0].boundingClientRect.bottom < 76;
      syncMobile();
    }, { rootMargin: "-76px 0px 0px 0px" }).observe(heroCta);
    new IntersectionObserver((entries) => {
      quoteVisible = entries[0].isIntersecting;
      syncMobile();
    }).observe(quote);
  }

  const form = $("quote-form");
  if (form) {
    const email = $("email");
    const phone = $("phone");
    let quoteStep = 1;
    const showQuoteStep = (step, focus = true) => {
      quoteStep = step;
      $("home-step").hidden = step !== 1;
      $("contact-step").hidden = step !== 2;
      $("quote-progress").textContent = `Step ${step} of 2 · ${step === 1 ? "Your home" : "Your details"}`;
      if (focus) $(step === 1 ? "zip" : "full-name").focus();
    };
    const homeIsValid = () => [...$("home-step").querySelectorAll("input,select")].every((input) => input.checkValidity());
    const continueQuote = () => {
      if (homeIsValid()) showQuoteStep(2);
      else [...$("home-step").querySelectorAll("input,select")].find((input) => !input.checkValidity()).reportValidity();
    };
    $("quote-continue").addEventListener("click", continueQuote);
    $("quote-back").addEventListener("click", () => showQuoteStep(1));
    showQuoteStep(1, false);
    const configured = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(QUOTE_EMAIL);
    if (configured) form.action = `https://formsubmit.co/${encodeURIComponent(QUOTE_EMAIL.trim())}`;
    if (/^https?:$/.test(location.protocol)) $("form-next").value = `${location.origin}${location.pathname}?quote=sent#quote`;
    else $("form-next").remove();
    $("form-submit").disabled = false;
    const validateContacts = () => {
      email.setCustomValidity("");
      phone.setCustomValidity("");
      if (!email.value.trim() && !phone.value.trim()) email.setCustomValidity("Please add a phone number or email so we can contact you.");
      if (phone.value.trim()) {
        const digits = phone.value.replace(/\D/g, "");
        if (digits.length < 7 || digits.length > 15 || /[A-Za-z]/.test(phone.value)) phone.setCustomValidity("Please enter a valid phone number.");
      }
    };
    [email, phone].forEach((input) => input.addEventListener("input", validateContacts));
    form.addEventListener("submit", (event) => {
      if (quoteStep === 1) { event.preventDefault(); continueQuote(); return; }
      if (!homeIsValid()) { event.preventDefault(); showQuoteStep(1); continueQuote(); return; }
      validateContacts();
      $("full-name").setCustomValidity($("full-name").value.trim() ? "" : "Please enter your name.");
      if (!form.reportValidity()) { event.preventDefault(); return; }
      if (!configured) {
        event.preventDefault();
        $("form-status").textContent = "Online quote requests are temporarily unavailable. Please call (304) 710-5430.";
        $("form-status").hidden = false;
        return;
      }
      if ($("website").value) { event.preventDefault(); return; }
      $("form-status").hidden = true;
      const params = new URLSearchParams(location.search);
      ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "fbclid"].forEach((key) => {
        if (params.get(key)) {
          let input = form.querySelector(`[name="${key}"]`);
          if (!input) {
            input = document.createElement("input");
            input.type = "hidden";
            input.name = key;
            form.append(input);
          }
          input.value = params.get(key).slice(0, 500);
        }
      });
      $("form-submit").disabled = true;
      $("form-submit").textContent = "Sending your request…";
    });
    $("full-name").addEventListener("input", () => $("full-name").setCustomValidity(""));
    window.addEventListener("pageshow", () => {
      $("form-submit").disabled = false;
      $("form-submit").innerHTML = 'Request My Cleaning Quote <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 12h15M13 6l6 6-6 6"/></svg>';
    });
    if (new URLSearchParams(location.search).get("quote") === "sent") {
      $("form-content").hidden = true;
      $("form-success").hidden = false;
    }
    $("new-request").addEventListener("click", () => {
      $("form-content").hidden = false;
      $("form-success").hidden = true;
      history.replaceState(null, "", `${location.pathname}#quote`);
      form.reset();
      showQuoteStep(1);
    });
  }

  const homeCarousel = $("home-carousel");
  if (homeCarousel) {
    const slides = [...homeCarousel.querySelectorAll(".photo-carousel-slide")];
    const dots = [...homeCarousel.querySelectorAll(".photo-dot")];
    const pauseButton = $("home-carousel-pause");
    let photoIndex = 0;
    let photoTimer = null;
    let photosPaused = reducedMotion.matches;
    const stopPhotos = () => { if (photoTimer) clearInterval(photoTimer); photoTimer = null; };
    const startPhotos = () => {
      stopPhotos();
      if (!photosPaused && !document.hidden && !homeCarousel.matches(":hover") && !homeCarousel.contains(document.activeElement)) {
        photoTimer = setInterval(() => showPhotoSlide(photoIndex + 1), 6000);
      }
    };
    const updatePhotoPause = () => {
      pauseButton.innerHTML = photosPaused
        ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m8 4 12 8-12 8z"/></svg>'
        : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 5v14M15 5v14"/></svg>';
      pauseButton.setAttribute("aria-label", photosPaused ? "Play automatic photos" : "Pause automatic photos");
    };
    const showPhotoSlide = (index, manual = false) => {
      photoIndex = (index + slides.length) % slides.length;
      slides.forEach((slide, i) => { slide.hidden = i !== photoIndex; });
      dots.forEach((dot, i) => {
        if (i === photoIndex) dot.setAttribute("aria-current", "true");
        else dot.removeAttribute("aria-current");
      });
      $("home-carousel-count").textContent = `${photoIndex + 1} / ${slides.length}`;
      if (manual) {
        const label = slides[photoIndex].getAttribute("aria-label") || `Photo ${photoIndex + 1}`;
        $("home-carousel-announcement").textContent = label;
        startPhotos();
      }
    };
    $("home-carousel-prev").addEventListener("click", () => showPhotoSlide(photoIndex - 1, true));
    $("home-carousel-next").addEventListener("click", () => showPhotoSlide(photoIndex + 1, true));
    pauseButton.addEventListener("click", () => { photosPaused = !photosPaused; updatePhotoPause(); startPhotos(); });
    dots.forEach((dot) => dot.addEventListener("click", () => showPhotoSlide(Number(dot.dataset.photoIndex), true)));
    homeCarousel.addEventListener("mouseenter", stopPhotos);
    homeCarousel.addEventListener("mouseleave", startPhotos);
    homeCarousel.addEventListener("focusin", stopPhotos);
    homeCarousel.addEventListener("focusout", () => requestAnimationFrame(startPhotos));
    homeCarousel.addEventListener("keydown", (event) => {
      if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
        event.preventDefault();
        showPhotoSlide(photoIndex + (event.key === "ArrowLeft" ? -1 : 1), true);
      }
    });
    let photoTouchX = null;
    let photoTouchY = null;
    homeCarousel.addEventListener("touchstart", (event) => {
      photoTouchX = event.touches[0].clientX;
      photoTouchY = event.touches[0].clientY;
      stopPhotos();
    }, { passive: true });
    homeCarousel.addEventListener("touchend", (event) => {
      if (photoTouchX !== null && event.changedTouches.length) {
        const dx = event.changedTouches[0].clientX - photoTouchX;
        const dy = event.changedTouches[0].clientY - photoTouchY;
        if (Math.abs(dx) > 45 && Math.abs(dx) > Math.abs(dy)) showPhotoSlide(photoIndex + (dx < 0 ? 1 : -1), true);
      }
      photoTouchX = null;
      photoTouchY = null;
      startPhotos();
    }, { passive: true });
    document.addEventListener("visibilitychange", startPhotos);
    reducedMotion.addEventListener("change", (event) => {
      if (event.matches) { photosPaused = true; updatePhotoPause(); }
      startPhotos();
    });
    showPhotoSlide(0);
    updatePhotoPause();
    startPhotos();
  }

  const quiz = $("q-form");
  if (quiz) {
    const steps = [...quiz.querySelectorAll(".quiz-step")];
    const total = steps.length;
    const phone = $("q-phone");
    const email = $("q-email");
    const name = $("q-full-name");
    const nextButton = $("q-next");
    const backButton = $("q-back");
    const submitButton = $("q-submit");
    let quizIndex = 0;
    const submitLabel = submitButton.innerHTML;
    const validateContacts = () => {
      email.setCustomValidity("");
      phone.setCustomValidity("");
      if (!email.value.trim() && !phone.value.trim()) email.setCustomValidity("Please add a phone number or email so we can contact you.");
      if (phone.value.trim()) {
        const digits = phone.value.replace(/\D/g, "");
        if (digits.length < 7 || digits.length > 15 || /[A-Za-z]/.test(phone.value)) phone.setCustomValidity("Please enter a valid phone number.");
      }
    };
    const validateName = () => {
      name.setCustomValidity(name.value.trim() ? "" : "Please enter your name.");
    };
    const showQuizStep = (index, focus = true) => {
      quizIndex = index;
      steps.forEach((step, i) => step.classList.toggle("is-current", i === index));
      const progressText = `Question ${index + 1} of ${total}`;
      const progressPct = `${((index + 1) / total) * 100}%`;
      $("q-progress").textContent = progressText;
      $("q-meter-bar").setAttribute("aria-valuenow", String(index + 1));
      $("q-meter-bar").setAttribute("aria-valuetext", progressText);
      $("q-meter").style.width = progressPct;
      $("q-soap").style.left = progressPct;
      backButton.hidden = index === 0;
      const last = index === total - 1;
      nextButton.hidden = last;
      submitButton.hidden = !last;
      if (focus) {
        const target = steps[index].querySelector("input, select, textarea");
        if (target) requestAnimationFrame(() => target.focus());
      }
    };
    const stepValid = (index, report = false) => {
      const step = steps[index];
      const restore = !step.classList.contains("is-current");
      step.classList.add("is-current");
      if (step.querySelector("#q-phone")) validateContacts();
      if (step.querySelector("#q-full-name")) validateName();
      const fields = [...step.querySelectorAll("input, select, textarea")].filter((input) => input.type !== "hidden" && !input.closest(".honeypot"));
      const bad = fields.find((input) => !input.checkValidity());
      if (bad) {
        if (report) bad.reportValidity();
        else if (restore) step.classList.remove("is-current");
        return false;
      }
      if (restore) step.classList.remove("is-current");
      return true;
    };
    nextButton.addEventListener("click", () => {
      if (stepValid(quizIndex, true)) showQuizStep(quizIndex + 1);
    });
    backButton.addEventListener("click", () => showQuizStep(quizIndex - 1));
    [email, phone].forEach((input) => input.addEventListener("input", validateContacts));
    name.addEventListener("input", () => name.setCustomValidity(""));
    const configured = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(QUOTE_EMAIL);
    quiz.addEventListener("submit", (event) => {
      if (quizIndex < total - 1) {
        event.preventDefault();
        if (stepValid(quizIndex, true)) showQuizStep(quizIndex + 1);
        return;
      }
      for (let i = 0; i < total; i += 1) {
        if (!stepValid(i, false)) {
          event.preventDefault();
          showQuizStep(i, false);
          stepValid(i, true);
          return;
        }
      }
      if ($("q-website").value) { event.preventDefault(); return; }
      if (!configured) {
        event.preventDefault();
        $("q-status").textContent = "Online quote requests are temporarily unavailable. Please call (304) 710-5430.";
        $("q-status").hidden = false;
        return;
      }
      $("q-status").hidden = true;
      const params = new URLSearchParams(location.search);
      ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "fbclid"].forEach((key) => {
        if (params.get(key)) {
          let input = quiz.querySelector(`[name="${key}"]`);
          if (!input) {
            input = document.createElement("input");
            input.type = "hidden";
            input.name = key;
            quiz.append(input);
          }
          input.value = params.get(key).slice(0, 500);
        }
      });
      submitButton.disabled = true;
      submitButton.textContent = "Sending your request…";
    });
    window.addEventListener("pageshow", () => {
      submitButton.disabled = false;
      submitButton.innerHTML = submitLabel;
    });
    $("q-new-request").addEventListener("click", () => {
      $("q-form-wrap").hidden = false;
      $("q-thanks").hidden = true;
      history.replaceState(null, "", location.pathname);
      quiz.reset();
      email.setCustomValidity("");
      phone.setCustomValidity("");
      name.setCustomValidity("");
      showQuizStep(0, true);
    });
    if (new URLSearchParams(location.search).has("sent")) {
      $("q-form-wrap").hidden = true;
      $("q-thanks").hidden = false;
    } else {
      showQuizStep(0, false);
    }
  }
})();

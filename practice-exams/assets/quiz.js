(function () {
  const COURSE_TITLE = "CS0023: Automata Theory and Formal Languages";
  const assetCatalog = {
    "product-cluster-1": {
      src: "../final-exam_reviewer_assets/page-37-image-1.png",
      alt: "State Machine Cluster 1 showing Machines 1-1 through 1-4.",
      caption: "State Machine Cluster 1. The Product Automata exam uses Machine 1-1 and Machine 1-2 from this cluster."
    },
    "moore-cluster-5": {
      src: "../final-exam_reviewer_assets/page-38-image-1.png",
      alt: "State Machine Cluster 5 showing Machines 5-1 and 5-2.",
      caption: "State Machine Cluster 5. Machine 5-1 is Moore-style because outputs appear on states, while Machine 5-2 uses transition labels."
    },
    "mealy-cluster-6": {
      src: "../final-exam_reviewer_assets/page-38-image-2.png",
      alt: "State Machine Cluster 6 showing Machines 6-1 and 6-2.",
      caption: "State Machine Cluster 6. The edge labels follow the Mealy convention input;output."
    },
    "pda-machine-8": {
      src: "../final-exam_reviewer_assets/page-38-image-3.png",
      alt: "Machine 8, a pushdown automaton with stack actions on its transitions.",
      caption: "Machine 8. The PDA pushes symbols while reading the first part of the input, then nondeterministically switches to matching pops."
    }
  };

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) {
      node.className = className;
    }
    if (text !== undefined) {
      node.textContent = text;
    }
    return node;
  }

  function createAssetFigure(assetKey) {
    const asset = assetCatalog[assetKey];
    if (!asset) {
      return null;
    }

    const figure = el("figure", "asset-figure");
    const image = document.createElement("img");
    image.src = asset.src;
    image.alt = asset.alt;
    image.loading = "lazy";

    const caption = el("figcaption", "", asset.caption);
    figure.append(image, caption);
    return figure;
  }

  function getDifficultyLabel(difficulty) {
    if (difficulty === "foundational") {
      return "Foundational recall";
    }
    if (difficulty === "application") {
      return "Application and comparison";
    }
    return "Tracing and reasoning";
  }

  function renderExam() {
    const data = window.examData;
    const root = document.getElementById("exam-root");
    if (!root || !data || !Array.isArray(data.questions)) {
      return;
    }

    const pageBanner = el("section", "page-banner");
    const headerTop = el("div", "page-header-top");
    const titleGroup = el("div");
    titleGroup.append(
      el("p", "course-kicker", COURSE_TITLE),
      el("p", "page-section-label", `Section ${data.sectionNumber}`),
      el("h1", "page-title", data.title)
    );

    const backLink = document.createElement("a");
    backLink.className = "back-link";
    backLink.href = "./index.html";
    backLink.textContent = "Back to exam index";

    headerTop.append(titleGroup, backLink);
    pageBanner.append(
      headerTop,
      el("p", "page-summary", data.summary)
    );

    const toolbar = el("section", "exam-toolbar");
    const toolbarCopy = el("div", "toolbar-copy");
    toolbarCopy.append(
      el("p", "exam-meta", `${data.questions.length} questions · all items on one page`),
      el("p", "", "Check each item for immediate feedback, or finish the whole exam for a page-level review.")
    );

    const toolbarActions = el("div", "toolbar-actions");
    const finishButton = document.createElement("button");
    finishButton.type = "button";
    finishButton.className = "toolbar-button primary";
    finishButton.textContent = "Finish exam";

    const retakeButton = document.createElement("button");
    retakeButton.type = "button";
    retakeButton.className = "toolbar-button secondary";
    retakeButton.textContent = "Retake exam";

    toolbarActions.append(finishButton, retakeButton);
    toolbar.append(toolbarCopy, toolbarActions);

    const form = document.createElement("form");
    form.noValidate = true;
    form.className = "question-list";

    const resultPanel = el("section", "result-panel");
    resultPanel.id = "exam-results";

    data.questions.forEach(function (question, index) {
      const article = el("article", "question-card");
      article.id = question.id;

      const head = el("div", "question-head");
      head.append(
        el("p", "question-meta", `Question ${index + 1}`),
        el("p", "question-meta difficulty-pill", getDifficultyLabel(question.difficulty))
      );

      article.append(head);

      const figure = createAssetFigure(question.assetKey);
      if (figure) {
        article.append(figure);
      }

      article.append(el("p", "question-prompt", question.prompt));

      const fieldset = el("fieldset", "option-list");
      fieldset.setAttribute("aria-label", `Options for question ${index + 1}`);

      question.options.forEach(function (optionText, optionIndex) {
        const wrapper = el("label", "option-item");
        const radio = document.createElement("input");
        radio.type = "radio";
        radio.name = question.id;
        radio.value = String(optionIndex);

        const optionBody = document.createElement("span");
        const optionLabel = el("span", "option-label", String.fromCharCode(65 + optionIndex) + ".");
        optionBody.append(optionLabel, document.createTextNode(" " + optionText));

        wrapper.append(radio, optionBody);
        fieldset.append(wrapper);
      });

      const checkButton = document.createElement("button");
      checkButton.type = "button";
      checkButton.className = "check-button";
      checkButton.textContent = "Check answer";
      checkButton.dataset.questionId = question.id;

      const feedback = el("div", "feedback");
      feedback.id = question.id + "-feedback";
      feedback.setAttribute("aria-live", "polite");

      article.append(fieldset, checkButton, feedback);
      form.append(article);
    });

    root.append(pageBanner, toolbar, form, resultPanel);

    function evaluateQuestion(questionId, options) {
      const selected = form.querySelector(`input[name="${questionId}"]:checked`);
      if (!selected) {
        return { state: "unanswered" };
      }

      const question = options.find(function (item) {
        return item.id === questionId;
      });
      const selectedIndex = Number(selected.value);
      const isCorrect = selectedIndex === question.correctIndex;
      const feedback = document.getElementById(questionId + "-feedback");

      feedback.className = "feedback is-visible " + (isCorrect ? "correct" : "incorrect");
      feedback.innerHTML = "";
      feedback.append(
        el("p", "feedback-status", isCorrect ? "Correct" : "Incorrect"),
        el(
          "p",
          "",
          `Answer: ${String.fromCharCode(65 + question.correctIndex)}. ${question.explanation}`
        )
      );

      return {
        state: isCorrect ? "correct" : "incorrect",
        selectedIndex: selectedIndex
      };
    }

    form.addEventListener("click", function (event) {
      const button = event.target.closest(".check-button");
      if (!button) {
        return;
      }
      evaluateQuestion(button.dataset.questionId, data.questions);
    });

    finishButton.addEventListener("click", function () {
      let correct = 0;
      const missed = [];
      const difficultyTotals = {
        foundational: { correct: 0, total: 0 },
        application: { correct: 0, total: 0 },
        reasoning: { correct: 0, total: 0 }
      };

      data.questions.forEach(function (question, index) {
        const outcome = evaluateQuestion(question.id, data.questions);
        difficultyTotals[question.difficulty].total += 1;

        if (outcome.state === "correct") {
          correct += 1;
          difficultyTotals[question.difficulty].correct += 1;
        } else {
          missed.push({ id: question.id, number: index + 1, unanswered: outcome.state === "unanswered" });
        }
      });

      const total = data.questions.length;
      const answered = total - missed.filter(function (item) { return item.unanswered; }).length;
      const accuracy = Math.round((correct / total) * 100);

      resultPanel.classList.add("is-visible");
      resultPanel.innerHTML = "";

      resultPanel.append(
        el("p", "result-meta", "Exam review"),
        el("h2", "", `${correct} / ${total} correct`)
      );

      const resultGrid = el("div", "result-grid");
      const scoreBox = el("div", "result-box");
      scoreBox.innerHTML = `<strong>${accuracy}%</strong><span>Overall accuracy</span>`;
      const answeredBox = el("div", "result-box");
      answeredBox.innerHTML = `<strong>${answered}</strong><span>Questions answered</span>`;
      const missedBox = el("div", "result-box");
      missedBox.innerHTML = `<strong>${missed.length}</strong><span>Missed or blank</span>`;
      resultGrid.append(scoreBox, answeredBox, missedBox);
      resultPanel.append(resultGrid);

      const review = el("p", "");
      review.textContent = buildReviewSummary(data.title, difficultyTotals, missed.length);
      resultPanel.append(review);

      if (missed.length > 0) {
        resultPanel.append(el("p", "result-meta", "Jump to missed questions"));
        const missedList = el("div", "missed-list");
        missed.forEach(function (item) {
          const link = document.createElement("a");
          link.className = "missed-link";
          link.href = `#${item.id}`;
          link.textContent = item.unanswered ? `Question ${item.number} (blank)` : `Question ${item.number}`;
          missedList.append(link);
        });
        resultPanel.append(missedList);
      }

      resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    });

    retakeButton.addEventListener("click", function () {
      form.reset();
      form.querySelectorAll(".feedback").forEach(function (node) {
        node.className = "feedback";
        node.innerHTML = "";
      });
      resultPanel.className = "result-panel";
      resultPanel.innerHTML = "";
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  function buildReviewSummary(title, totals, missedCount) {
    const tiers = [
      `Foundational items: ${totals.foundational.correct}/${totals.foundational.total}`,
      `Application items: ${totals.application.correct}/${totals.application.total}`,
      `Reasoning items: ${totals.reasoning.correct}/${totals.reasoning.total}`
    ];

    if (missedCount === 0) {
      return `${title}: complete mastery on this attempt. ${tiers.join(". ")}.`;
    }

    if (missedCount <= 4) {
      return `${title}: strong overall performance with a short review still worth doing. ${tiers.join(". ")}.`;
    }

    if (missedCount <= 9) {
      return `${title}: workable command of the topic, but the missed questions show a few gaps in notation, interpretation, or construction steps. ${tiers.join(". ")}.`;
    }

    return `${title}: this topic needs another pass through the summary and the missed explanations before exam day. ${tiers.join(". ")}.`;
  }

  document.addEventListener("DOMContentLoaded", renderExam);
})();

import Chart from "chart.js/auto";


/* ============================================================
   API ENDPOINTS
   ============================================================ */
const API_BASE_URL =
  "https://ai-cicd-devsecops-assistant.onrender.com";

const API_URL =
  `${API_BASE_URL}/api/dashboard/overview`;

const PIPELINE_HISTORY_URL =
  `${API_BASE_URL}/api/pipelines`;

/* ============================================================
   DOM ELEMENTS
   ============================================================ */

const refreshBtn =
  document.getElementById("refreshBtn");

const cards =
  document.querySelectorAll(".card");

const panels =
  document.querySelectorAll(".panel");

const apiDot =
  document.getElementById("apiDot");

const apiLabel =
  document.getElementById("apiLabel");

const lastUpdated =
  document.getElementById("lastUpdated");

const deployStage =
  document.getElementById("deployStage");


/* ============================================================
   CHART VARIABLES
   ============================================================ */

let failureChart = null;
let securityChart = null;
let buildTimeChart = null;
let cpuChart = null;
let memoryChart = null;


/* ============================================================
   THEME COLORS FROM CSS
   ============================================================ */

const rootStyles =
  getComputedStyle(document.documentElement);

function cssColor(variableName, fallback) {
  return (
    rootStyles
      .getPropertyValue(variableName)
      .trim() || fallback
  );
}

const chartColors = {
  text:
    cssColor(
      "--text-secondary",
      "#8b96a5"
    ),

  border:
    cssColor(
      "--border-soft",
      "#171e29"
    ),

  accent:
    cssColor(
      "--accent",
      "#2dd4ee"
    ),

  good:
    cssColor(
      "--good",
      "#3ddc97"
    ),

  medium:
    cssColor(
      "--medium",
      "#ffd166"
    ),

  high:
    cssColor(
      "--high",
      "#ff9b45"
    ),

  critical:
    cssColor(
      "--critical",
      "#f0466b"
    )
};


/* ============================================================
   RISK HELPERS
   ============================================================ */

function riskLevel(value) {
  const v =
    String(value ?? "")
      .toLowerCase();

  if (
    [
      "critical",
      "fail",
      "failed",
      "failure"
    ].some((word) => v.includes(word))
  ) {
    return "critical";
  }

  if (
    [
      "high",
      "at risk",
      "unstable"
    ].some((word) => v.includes(word))
  ) {
    return "high";
  }

  if (
    [
      "medium",
      "moderate",
      "warning"
    ].some((word) => v.includes(word))
  ) {
    return "medium";
  }

  if (
    [
      "minimal",
      "safe",
      "low",
      "good",
      "success",
      "passed",
      "healthy",
      "stable"
    ].some((word) => v.includes(word))
  ) {
    return "good";
  }

  return null;
}


/* ============================================================
   PERCENTAGE LEVEL
   ============================================================ */

function levelFromPercent(
  percent,
  invert = false
) {
  const p = Math.max(
    0,
    Math.min(
      100,
      Number(percent) || 0
    )
  );

  /*
    invert = true
    Higher number = better
    Example: Security Score
  */

  if (invert) {
    if (p >= 80) {
      return "good";
    }

    if (p >= 60) {
      return "medium";
    }

    if (p >= 35) {
      return "high";
    }

    return "critical";
  }


  /*
    Higher number = worse
    Example:
    Failure Probability
    CPU Usage
  */

  if (p >= 80) {
    return "critical";
  }

  if (p >= 60) {
    return "high";
  }

  if (p >= 35) {
    return "medium";
  }

  return "good";
}


/* ============================================================
   SET BADGE
   ============================================================ */

function setBadge(
  id,
  rawValue
) {
  const element =
    document.getElementById(id);

  if (!element) {
    return;
  }

  element.textContent =
    rawValue ?? "-";

  element.className =
    "badge";

  const level =
    riskLevel(rawValue);

  if (level) {
    element.classList.add(
      `level-${level}`
    );
  }
}


/* ============================================================
   SET PROGRESS BAR
   ============================================================ */

function setBar(
  id,
  percent,
  invert = false
) {
  const element =
    document.getElementById(id);

  if (!element) {
    return;
  }

  const clamped =
    Math.max(
      0,
      Math.min(
        100,
        Number(percent) || 0
      )
    );

  element.style.width =
    `${clamped}%`;

  element.className =
    "bar-fill";

  const level =
    levelFromPercent(
      clamped,
      invert
    );

  element.classList.add(
    `level-${level}`
  );
}


/* ============================================================
   STATUS DOT
   ============================================================ */

function setStatusDot(
  id,
  rawStatus
) {
  const element =
    document.getElementById(id);

  if (!element) {
    return;
  }

  const value =
    String(rawStatus ?? "")
      .toLowerCase();

  element.className =
    "dot";

  if (
    [
      "success",
      "passed",
      "healthy",
      "running",
      "good"
    ].some((word) =>
      value.includes(word)
    )
  ) {
    element.classList.add(
      "dot-good"
    );
  }

  else if (
    [
      "fail",
      "failed",
      "error",
      "critical"
    ].some((word) =>
      value.includes(word)
    )
  ) {
    element.classList.add(
      "dot-bad"
    );
  }

  else if (
    [
      "warning",
      "degraded",
      "medium"
    ].some((word) =>
      value.includes(word)
    )
  ) {
    element.classList.add(
      "dot-medium"
    );
  }

  else {
    element.classList.add(
      "dot-idle"
    );
  }
}


/* ============================================================
   LOADING STATE
   ============================================================ */

function setLoading(isLoading) {
  cards.forEach((card) => {
    card.classList.toggle(
      "loading",
      isLoading
    );
  });

  panels.forEach((panel) => {
    panel.classList.toggle(
      "loading",
      isLoading
    );
  });

  if (refreshBtn) {
    refreshBtn.classList.toggle(
      "loading",
      isLoading
    );

    refreshBtn.disabled =
      isLoading;
  }
}


/* ============================================================
   API CONNECTION
   ============================================================ */

function setApiConnection(connected) {
  if (
    !apiDot ||
    !apiLabel
  ) {
    return;
  }

  apiDot.className =
    "dot";

  apiDot.classList.add(
    connected
      ? "dot-good"
      : "dot-bad"
  );

  apiLabel.textContent =
    connected
      ? "API Connected"
      : "API Offline";
}


/* ============================================================
   LAST UPDATED TIME
   ============================================================ */

function stampUpdatedTime() {
  if (!lastUpdated) {
    return;
  }

  const now =
    new Date();

  lastUpdated.textContent =
    `Updated ${now.toLocaleTimeString(
      [],
      {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit"
      }
    )}`;
}


/* ============================================================
   DEPLOYMENT STAGE
   ============================================================ */

function updateDeploymentStage(data) {
  if (!deployStage) {
    return;
  }

  deployStage.classList.remove(
    "completed",
    "failed"
  );

  const pipelineStatus = String(
    data?.pipeline?.status ?? ""
  ).toLowerCase();

  const testsFailed = Number(
    data?.pipeline?.tests_failed ?? 0
  );

  const criticalCount = Number(
    data?.security?.critical ?? 0
  );

  const overallRisk = String(
    data?.overall_risk ?? ""
  ).toLowerCase();

  const deploymentAllowed =
    data?.deployment?.allowed;

  const pipelineFailed =
    pipelineStatus.includes("fail") ||
    pipelineStatus.includes("error") ||
    testsFailed > 0;

  const blocked =
    deploymentAllowed === false ||
    pipelineFailed ||
    criticalCount > 0 ||
    overallRisk === "critical";

  if (blocked) {
    deployStage.classList.add("failed");
  } else {
    deployStage.classList.add("completed");
  }
}


/* ============================================================
   CHART HELPERS
   ============================================================ */

function destroyChart(chart) {
  if (chart) {
    chart.destroy();
  }
}


function getCanvas(id) {
  return document.getElementById(id);
}


/* ============================================================
   COMMON LINE CHART OPTIONS
   ============================================================ */

function createLineOptions(
  maxValue = undefined
) {
  return {
    responsive: true,

    maintainAspectRatio: false,

    interaction: {
      intersect: false,
      mode: "index"
    },

    plugins: {
      legend: {
        labels: {
          color:
            chartColors.text,

          usePointStyle:
            true
        }
      }
    },

    scales: {
      x: {
        ticks: {
          color:
            chartColors.text
        },

        grid: {
          color:
            chartColors.border
        }
      },

      y: {
        beginAtZero:
          true,

        max:
          maxValue,

        ticks: {
          color:
            chartColors.text
        },

        grid: {
          color:
            chartColors.border
        }
      }
    }
  };
}


/* ============================================================
   FAILURE PROBABILITY CHART
   ============================================================ */

function createFailureChart(data) {
  const canvas =
    getCanvas("failureChart");

  if (!canvas) {
    return;
  }

  destroyChart(
    failureChart
  );

  const failure =
    Math.max(
      0,
      Math.min(
        100,
        Number(
          data?.ml_prediction
            ?.failure_probability
        ) || 0
      )
    );

  const success =
    Math.max(
      0,
      100 - failure
    );

  failureChart =
    new Chart(
      canvas,
      {
        type:
          "doughnut",

        data: {
          labels: [
            "Failure",
            "Success"
          ],

          datasets: [
            {
              data: [
                failure,
                success
              ],

              backgroundColor: [
                chartColors.critical,
                chartColors.good
              ],

              borderWidth:
                0
            }
          ]
        },

        options: {
          responsive:
            true,

          maintainAspectRatio:
            false,

          cutout:
            "70%",

          plugins: {
            legend: {
              position:
                "bottom",

              labels: {
                color:
                  chartColors.text,

                usePointStyle:
                  true,

                padding:
                  18
              }
            },

            tooltip: {
              callbacks: {
                label(context) {
                  return (
                    `${context.label}: ` +
                    `${context.raw}%`
                  );
                }
              }
            }
          }
        }
      }
    );
}


/* ============================================================
   SECURITY SEVERITY CHART
   ============================================================ */

function createSecurityChart(data) {
  const canvas =
    getCanvas("securityChart");

  if (!canvas) {
    return;
  }

  destroyChart(
    securityChart
  );

  securityChart =
    new Chart(
      canvas,
      {
        type:
          "bar",

        data: {
          labels: [
            "Critical",
            "High",
            "Medium",
            "Low"
          ],

          datasets: [
            {
              label:
                "Issues",

              data: [
                data?.security
                  ?.critical ?? 0,

                data?.security
                  ?.high ?? 0,

                data?.security
                  ?.medium ?? 0,

                data?.security
                  ?.low ?? 0
              ],

              backgroundColor: [
                chartColors.critical,
                chartColors.high,
                chartColors.medium,
                chartColors.good
              ],

              borderRadius:
                5
            }
          ]
        },

        options: {
          responsive:
            true,

          maintainAspectRatio:
            false,

          plugins: {
            legend: {
              display:
                false
            }
          },

          scales: {
            x: {
              ticks: {
                color:
                  chartColors.text
              },

              grid: {
                display:
                  false
              }
            },

            y: {
              beginAtZero:
                true,

              ticks: {
                color:
                  chartColors.text,

                precision:
                  0,

                stepSize:
                  1
              },

              grid: {
                color:
                  chartColors.border
              }
            }
          }
        }
      }
    );
}


/* ============================================================
   LOAD PIPELINE HISTORY
   ============================================================ */

async function loadPipelineCharts() {
  try {
    const response =
      await fetch(
        PIPELINE_HISTORY_URL
      );

    if (!response.ok) {
      throw new Error(
        `Pipeline API returned ${response.status}`
      );
    }

    const pipelines =
      await response.json();

    if (
      !Array.isArray(pipelines) ||
      pipelines.length === 0
    ) {
      console.log(
        "No pipeline history available."
      );

      return;
    }


    /*
      Backend returns latest records first.
      Take latest 8 and reverse them
      so graphs display oldest -> newest.
    */

    const recent =
      pipelines
        .slice(0, 8)
        .reverse();


    const labels =
      recent.map(
        (run) =>
          `#${run.pipeline_id}`
      );


    createBuildTimeChart(
      labels,
      recent
    );

    createCpuChart(
      labels,
      recent
    );

    createMemoryChart(
      labels,
      recent
    );
  }

  catch (error) {
    console.error(
      "Pipeline chart error:",
      error
    );
  }
}


/* ============================================================
   BUILD TIME CHART
   ============================================================ */

function createBuildTimeChart(
  labels,
  pipelines
) {
  const canvas =
    getCanvas(
      "buildTimeChart"
    );

  if (!canvas) {
    return;
  }

  destroyChart(
    buildTimeChart
  );

  buildTimeChart =
    new Chart(
      canvas,
      {
        type:
          "line",

        data: {
          labels,

          datasets: [
            {
              label:
                "Build Time (sec)",

              data:
                pipelines.map(
                  (run) =>
                    Number(
                      run.build_time
                    ) || 0
                ),

              borderColor:
                chartColors.accent,

              backgroundColor:
                chartColors.accent,

              pointBackgroundColor:
                chartColors.accent,

              tension:
                0.3,

              borderWidth:
                2
            }
          ]
        },

        options:
          createLineOptions()
      }
    );
}


/* ============================================================
   CPU CHART
   ============================================================ */

function createCpuChart(
  labels,
  pipelines
) {
  const canvas =
    getCanvas(
      "cpuChart"
    );

  if (!canvas) {
    return;
  }

  destroyChart(
    cpuChart
  );

  cpuChart =
    new Chart(
      canvas,
      {
        type:
          "line",

        data: {
          labels,

          datasets: [
            {
              label:
                "CPU Usage (%)",

              data:
                pipelines.map(
                  (run) =>
                    Number(
                      run.cpu_usage
                    ) || 0
                ),

              borderColor:
                chartColors.medium,

              backgroundColor:
                chartColors.medium,

              pointBackgroundColor:
                chartColors.medium,

              tension:
                0.3,

              borderWidth:
                2
            }
          ]
        },

        options:
          createLineOptions(
            100
          )
      }
    );
}


/* ============================================================
   MEMORY CHART
   ============================================================ */

function createMemoryChart(
  labels,
  pipelines
) {
  const canvas =
    getCanvas(
      "memoryChart"
    );

  if (!canvas) {
    return;
  }

  destroyChart(
    memoryChart
  );

  memoryChart =
    new Chart(
      canvas,
      {
        type:
          "line",

        data: {
          labels,

          datasets: [
            {
              label:
                "Memory Usage (MB)",

              data:
                pipelines.map(
                  (run) =>
                    Number(
                      run.memory_usage
                    ) || 0
                ),

              borderColor:
                chartColors.good,

              backgroundColor:
                chartColors.good,

              pointBackgroundColor:
                chartColors.good,

              tension:
                0.3,

              borderWidth:
                2
            }
          ]
        },

        options:
          createLineOptions()
      }
    );
}


/* ============================================================
   MAIN DASHBOARD
   ============================================================ */

async function loadDashboard() {
  setLoading(true);

  try {
    const response =
      await fetch(
        API_URL
      );

    if (!response.ok) {
      throw new Error(
        `Dashboard API returned ${response.status}`
      );
    }

    const data =
      await response.json();

    console.log(
      "Dashboard data:",
      data
    );


    /* ========================================================
       PIPELINE
       ======================================================== */

    const buildStatus =
      document.getElementById(
        "buildStatus"
      );

    if (buildStatus) {
      buildStatus.textContent =
        data?.pipeline?.status
        ?? "No data";
    }


    setStatusDot(
      "buildStatusDot",
      data?.pipeline?.status
    );


    const buildTime =
      document.getElementById(
        "buildTime"
      );

    if (buildTime) {
      buildTime.textContent =
        `${
          data?.pipeline?.build_time
          ?? 0
        } sec`;
    }


    const cpuUsage =
      document.getElementById(
        "cpuUsage"
      );

    if (cpuUsage) {
      cpuUsage.textContent =
        `${
          data?.pipeline?.cpu_usage
          ?? 0
        }%`;
    }


    setBar(
      "cpuUsageBar",
      data?.pipeline?.cpu_usage
      ?? 0
    );


    const memoryUsage =
      document.getElementById(
        "memoryUsage"
      );

    if (memoryUsage) {
      memoryUsage.textContent =
        `${
          data?.pipeline?.memory_usage
          ?? 0
        } MB`;
    }


    /* ========================================================
       ML PREDICTION
       ======================================================== */

    const failureProbability =
      Number(
        data?.ml_prediction
          ?.failure_probability
      ) || 0;


    const failureProbabilityText =
      document.getElementById(
        "failureProbability"
      );

    if (failureProbabilityText) {
      failureProbabilityText.textContent =
        `${failureProbability}%`;
    }


    setBar(
      "failureProbabilityBar",
      failureProbability
    );


    const predictedStatus =
      document.getElementById(
        "predictedStatus"
      );

    if (predictedStatus) {
      predictedStatus.textContent =
        data?.ml_prediction
          ?.predicted_status
        ?? "No prediction";
    }


    const confidence =
      document.getElementById(
        "confidence"
      );

    if (confidence) {
      confidence.textContent =
        `${
          data?.ml_prediction
            ?.confidence
          ?? 0
        }%`;
    }


    setBadge(
      "predictionRisk",
      data?.ml_prediction
        ?.risk_level
      ?? "No data"
    );


    /* ========================================================
       SECURITY
       ======================================================== */

    const securityScore =
      Number(
        data?.security
          ?.security_score
      ) || 0;


    const securityScoreElement =
      document.getElementById(
        "securityScore"
      );

    if (securityScoreElement) {
      securityScoreElement.textContent =
        securityScore;
    }


    setBar(
      "securityScoreBar",
      securityScore,
      true
    );


    const vulnerabilities =
      document.getElementById(
        "vulnerabilities"
      );

    if (vulnerabilities) {
      vulnerabilities.textContent =
        data?.security
          ?.vulnerabilities
        ?? 0;
    }


    const critical =
      document.getElementById(
        "critical"
      );

    if (critical) {
      critical.textContent =
        data?.security?.critical
        ?? 0;
    }


    const high =
      document.getElementById(
        "high"
      );

    if (high) {
      high.textContent =
        data?.security?.high
        ?? 0;
    }


    const medium =
      document.getElementById(
        "medium"
      );

    if (medium) {
      medium.textContent =
        data?.security?.medium
        ?? 0;
    }


    const low =
      document.getElementById(
        "low"
      );

    if (low) {
      low.textContent =
        data?.security?.low
        ?? 0;
    }


    /* ========================================================
       COMPLEXITY
       ======================================================== */

    const complexityFile =
      document.getElementById(
        "complexityFile"
      );

    if (complexityFile) {
      complexityFile.textContent =
        data?.complexity?.file
        ?? "-";
    }


    const timeComplexity =
      document.getElementById(
        "timeComplexity"
      );

    if (timeComplexity) {
      timeComplexity.textContent =
        data?.complexity
          ?.time_complexity
        ?? "Not analyzed";
    }


    const spaceComplexity =
      document.getElementById(
        "spaceComplexity"
      );

    if (spaceComplexity) {
      spaceComplexity.textContent =
        data?.complexity
          ?.space_complexity
        ?? "Not analyzed";
    }


    /* ========================================================
       OVERALL RISK
       ======================================================== */

const actualPipelineFailed =
  String(
    data.pipeline?.status ?? ""
  )
    .toLowerCase()
    .includes("fail")
  ||
  Number(
    data.pipeline?.tests_failed ?? 0
  ) > 0;

const displayedOverallRisk =
  actualPipelineFailed
    ? "High"
    : (
        data.overall_risk
        ?? "No data"
      );

setBadge(
  "overallRisk",
  displayedOverallRisk
);

    /* ========================================================
       DEPLOYMENT
       ======================================================== */

    updateDeploymentStage(
      data
    );


    /* ========================================================
       CHARTS
       ======================================================== */

    createFailureChart(
      data
    );

    createSecurityChart(
      data
    );

    await loadPipelineCharts();


    /* ========================================================
       API STATUS
       ======================================================== */

    setApiConnection(
      true
    );

    stampUpdatedTime();
  }


  catch (error) {
    console.error(
      "Dashboard error:",
      error
    );


    const buildStatus =
      document.getElementById(
        "buildStatus"
      );

    if (buildStatus) {
      buildStatus.textContent =
        "Backend Offline";
    }


    setStatusDot(
      "buildStatusDot",
      "failed"
    );


    setApiConnection(
      false
    );


    if (lastUpdated) {
      lastUpdated.textContent =
        "Update failed";
    }


    if (deployStage) {
      deployStage.classList.remove(
        "completed"
      );

      deployStage.classList.add(
        "failed"
      );
    }
  }


  finally {
    setLoading(
      false
    );
  }
}


/* ============================================================
   EVENTS
   ============================================================ */

if (refreshBtn) {
  refreshBtn.addEventListener(
    "click",
    loadDashboard
  );
}


/* ============================================================
   INITIAL LOAD
   ============================================================ */

loadDashboard();
document.addEventListener("DOMContentLoaded", function () {

    const fileInput =
        document.getElementById("image");

    const uploadZone =
        document.getElementById("uploadZone");

    const uploadPlaceholder =
        document.getElementById("uploadPlaceholder");

    const previewContainer =
        document.getElementById("previewContainer");

    const imagePreview =
        document.getElementById("imagePreview");

    const fileName =
        document.getElementById("fileName");

    const uploadForm =
        document.getElementById("uploadForm");

    const analyzeButton =
        document.getElementById("analyzeButton");


    // ========================================================
    // CLICK UPLOAD AREA
    // ========================================================

    if (uploadZone && fileInput) {

        uploadZone.addEventListener(
            "click",
            function (event) {

                if (
                    event.target.closest(
                        ".preview-container"
                    )
                ) {
                    return;
                }

                fileInput.click();

            }
        );

    }


    // ========================================================
    // FILE SELECTED
    // ========================================================

    if (fileInput) {

        fileInput.addEventListener(
            "change",
            function () {

                if (
                    this.files &&
                    this.files.length > 0
                ) {

                    showPreview(
                        this.files[0]
                    );

                }

            }
        );

    }


    // ========================================================
    // PREVIEW
    // ========================================================

    function showPreview(file) {

        if (!file.type.startsWith("image/")) {

            alert(
                "Please select a valid image file."
            );

            return;

        }


        const reader =
            new FileReader();


        reader.onload = function (event) {

            imagePreview.src =
                event.target.result;

            fileName.textContent =
                file.name;

            if (uploadPlaceholder) {

                uploadPlaceholder.style.display =
                    "none";

            }

            if (previewContainer) {

                previewContainer.classList.add(
                    "show"
                );

            }

            if (uploadZone) {

                uploadZone.classList.add(
                    "has-image"
                );

            }

        };


        reader.readAsDataURL(file);

    }


    // ========================================================
    // DRAG & DROP
    // ========================================================

    if (uploadZone) {

        uploadZone.addEventListener(
            "dragover",
            function (event) {

                event.preventDefault();

                uploadZone.classList.add(
                    "dragover"
                );

            }
        );


        uploadZone.addEventListener(
            "dragleave",
            function () {

                uploadZone.classList.remove(
                    "dragover"
                );

            }
        );


        uploadZone.addEventListener(
            "drop",
            function (event) {

                event.preventDefault();

                uploadZone.classList.remove(
                    "dragover"
                );


                const files =
                    event.dataTransfer.files;


                if (
                    files &&
                    files.length > 0
                ) {

                    try {

                        fileInput.files =
                            files;

                    } catch (error) {

                        console.log(
                            "Could not assign dropped file."
                        );

                    }

                    showPreview(
                        files[0]
                    );

                }

            }
        );

    }


    // ========================================================
    // FORM SUBMIT
    // ========================================================

    if (uploadForm) {

        uploadForm.addEventListener(
            "submit",
            function () {

                if (!fileInput.files.length) {

                    alert(
                        "Please select an image first."
                    );

                    return;

                }


                if (analyzeButton) {

                    analyzeButton.disabled =
                        true;

                    analyzeButton.innerHTML =
                        `
                        <span class="button-spinner"></span>
                        Analyzing...
                        `;

                }

            }
        );

    }

});

// ========================================================
// PREDICTION PROBABILITY BARS
// ========================================================

document.querySelectorAll(".probability-fill").forEach(function (bar) {

    const width = parseFloat(
        bar.getAttribute("data-width")
    );

    if (!isNaN(width)) {
        bar.style.width = width + "%";
    }

});

// ============================================================
// PERFORMANCE PAGE CHARTS
// ============================================================

document.addEventListener("DOMContentLoaded", function () {

    if (typeof Chart === "undefined") {
        return;
    }


    // ========================================================
    // CLASSIFICATION METRICS
    // ========================================================

    const classMetricsCanvas =
        document.getElementById("classMetricsChart");

    if (classMetricsCanvas) {

        new Chart(classMetricsCanvas, {

            type: "bar",

            data: {

                labels: [
                    "Benign",
                    "Malignant",
                    "Normal"
                ],

                datasets: [

                    {
                        label: "Precision",

                        data: [
                            94.44,
                            98.82,
                            98.36
                        ],

                        borderWidth: 0,

                        borderRadius: 7
                    },

                    {
                        label: "Recall",

                        data: [
                            94.44,
                            100.00,
                            96.77
                        ],

                        borderWidth: 0,

                        borderRadius: 7
                    },

                    {
                        label: "F1 Score",

                        data: [
                            94.44,
                            99.41,
                            97.56
                        ],

                        borderWidth: 0,

                        borderRadius: 7
                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    y: {

                        beginAtZero: true,

                        max: 100,

                        ticks: {

                            callback: function (value) {
                                return value + "%";
                            }

                        }

                    }

                },

                plugins: {

                    legend: {
                        position: "bottom"
                    },

                    tooltip: {

                        callbacks: {

                            label: function (context) {

                                return (
                                    context.dataset.label +
                                    ": " +
                                    context.parsed.y.toFixed(2) +
                                    "%"
                                );

                            }

                        }

                    }

                }

            }

        });

    }


    // ========================================================
    // CLASS DISTRIBUTION
    // ========================================================

    const distributionCanvas =
        document.getElementById(
            "classDistributionChart"
        );

    if (distributionCanvas) {

        new Chart(distributionCanvas, {

            type: "doughnut",

            data: {

                labels: [
                    "Benign",
                    "Malignant",
                    "Normal"
                ],

                datasets: [

                    {

                        data: [
                            18,
                            84,
                            62
                        ],

                        borderWidth: 3,

                        hoverOffset: 8

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                cutout: "68%",

                plugins: {

                    legend: {

                        position: "bottom",

                        labels: {

                            padding: 18,

                            usePointStyle: true

                        }

                    }

                }

            }

        });

    }


    // ========================================================
    // CONFUSION MATRIX
    // ========================================================

    const confusionCanvas =
        document.getElementById(
            "confusionMatrixChart"
        );

    if (confusionCanvas) {

        new Chart(confusionCanvas, {

            type: "bar",

            data: {

                labels: [
                    "Benign",
                    "Malignant",
                    "Normal"
                ],

                datasets: [

                    {
                        label: "Correct",

                        data: [
                            17,
                            84,
                            60
                        ],

                        borderRadius: 7,

                        borderWidth: 0
                    },

                    {
                        label: "Incorrect",

                        data: [
                            1,
                            0,
                            2
                        ],

                        borderRadius: 7,

                        borderWidth: 0
                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    x: {
                        stacked: true
                    },

                    y: {

                        stacked: true,

                        beginAtZero: true,

                        ticks: {
                            precision: 0
                        }

                    }

                },

                plugins: {

                    legend: {
                        position: "bottom"
                    }

                }

            }

        });

    }


    // ========================================================
    // CORRECT / INCORRECT
    // ========================================================

    const accuracyCanvas =
        document.getElementById(
            "predictionAccuracyChart"
        );

    if (accuracyCanvas) {

        new Chart(accuracyCanvas, {

            type: "doughnut",

            data: {

                labels: [
                    "Correct",
                    "Incorrect"
                ],

                datasets: [

                    {

                        data: [
                            161,
                            3
                        ],

                        borderWidth: 3,

                        hoverOffset: 8

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                cutout: "72%",

                plugins: {

                    legend: {

                        position: "bottom",

                        labels: {
                            usePointStyle: true
                        }

                    },

                    tooltip: {

                        callbacks: {

                            label: function (context) {

                                const total =
                                    context.dataset.data
                                        .reduce(
                                            (a, b) => a + b,
                                            0
                                        );

                                const value =
                                    context.raw;

                                const percentage =
                                    (
                                        value /
                                        total *
                                        100
                                    ).toFixed(2);

                                return (
                                    context.label +
                                    ": " +
                                    value +
                                    " (" +
                                    percentage +
                                    "%)"
                                );

                            }

                        }

                    }

                }

            }

        });

    }


    // ========================================================
    // OVERALL MODEL PROFILE
    // ========================================================

    const profileCanvas =
        document.getElementById(
            "modelProfileChart"
        );

    if (profileCanvas) {

        new Chart(profileCanvas, {

            type: "radar",

            data: {

                labels: [
                    "Accuracy",
                    "Precision",
                    "Recall",
                    "F1 Score"
                ],

                datasets: [

                    {

                        label: "ResNet18",

                        data: [
                            98.17,
                            97.21,
                            97.07,
                            97.14
                        ],

                        borderWidth: 2,

                        pointRadius: 4,

                        fill: true

                    }

                ]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                scales: {

                    r: {

                        beginAtZero: true,

                        min: 80,

                        max: 100,

                        ticks: {

                            stepSize: 5

                        }

                    }

                },

                plugins: {

                    legend: {

                        position: "bottom"

                    }

                }

            }

        });

    }

});
allprojects {
    configurations.all {
        resolutionStrategy.eachDependency {
            if (requested.group == "com.github.kittinunf.result" && requested.name == "result" && requested.version == "3.0.0") {
                useVersion("3.0.1")
                because("Transitive dependency of Scabbard, currently not available on mavenCentral()")
            }
        }
    }
}

plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.jetbrains.kotlin.android) version "2.0.21"
    alias(libs.plugins.compose.compiler)

    kotlin("plugin.serialization") version "1.9.24"
    id("com.google.devtools.ksp")
    id("scabbard.gradle") version "0.5.0"
}

android {
    namespace = "com.milikovv.interfacecollector"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.milikovv.interfacecollector"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        compose = true
    }
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.1"
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }

    scabbard {
        enabled = true
        outputFormat = "svg"
    }
}

dependencies {

    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.6.4")
    implementation("com.github.kittinunf.result:result:3.0.0")
    implementation(project(":rtmp_muxer"))
    implementation("com.google.dagger:dagger:2.52")
    implementation("com.google.dagger:dagger-android:2.52")
    implementation("com.google.dagger:dagger-android-support:2.52")
    ksp(libs.dagger.compiler)
    ksp(libs.dagger.android.processor)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
    debugImplementation(libs.androidx.ui.tooling)
    debugImplementation(libs.androidx.ui.test.manifest)
}
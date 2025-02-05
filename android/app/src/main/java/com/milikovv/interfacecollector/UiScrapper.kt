package com.milikovv.interfacecollector

import android.app.Application
import com.milikovv.interfacecollector.dagger.DaggerAppComponent
import dagger.android.AndroidInjector
import dagger.android.DispatchingAndroidInjector
import dagger.android.HasAndroidInjector
import javax.inject.Inject

class UiScrapper: Application(), HasAndroidInjector {
    @Inject
    lateinit var androidInjector : DispatchingAndroidInjector<Any>

    override fun androidInjector(): AndroidInjector<Any> = androidInjector

    override fun onCreate() {
        super.onCreate()

        DaggerAppComponent.builder().application(this)!!.build()!!.inject(this)
    }
}
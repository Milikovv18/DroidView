package com.milikovv.interfacecollector.consumers

import javax.inject.Singleton

@Singleton
interface Consumer {
    fun consume(data : Any)
}

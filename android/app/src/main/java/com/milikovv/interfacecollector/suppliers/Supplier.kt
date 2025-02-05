package com.milikovv.interfacecollector.suppliers

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableSharedFlow

interface Supplier<T> {
    fun getHotStream() : MutableSharedFlow<T>
    fun getOnce(callback : ((T?) -> Unit))
}

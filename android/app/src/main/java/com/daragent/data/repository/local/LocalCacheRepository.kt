package com.daragent.data.repository.local

import com.daragent.data.local.DarAgentDatabase
import com.daragent.data.local.dao.EntitlementDao
import com.daragent.data.local.dao.PaymentDao
import com.daragent.data.local.dao.ProjectDao
import com.daragent.data.local.dao.WalletDao
import com.daragent.data.local.entity.EntitlementEntity
import com.daragent.data.local.entity.PaymentEntity
import com.daragent.data.local.entity.ProjectEntity
import com.daragent.data.local.entity.WalletEntity
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

class LocalCacheRepository(private val database: DarAgentDatabase) {
    private val walletDao: WalletDao = database.walletDao()
    private val entitlementDao: EntitlementDao = database.entitlementDao()
    private val projectDao: ProjectDao = database.projectDao()
    private val paymentDao: PaymentDao = database.paymentDao()

    suspend fun cacheWallet(wallet: WalletEntity) = walletDao.insert(wallet)
    suspend fun getWallet(userId: String) = walletDao.get(userId)

    suspend fun cacheEntitlement(entitlement: EntitlementEntity) = entitlementDao.insert(entitlement)
    suspend fun listEntitlements(userId: String) = entitlementDao.list(userId)

    suspend fun cacheProject(project: ProjectEntity) = projectDao.insert(project)
    suspend fun listProjects(userId: String) = projectDao.list(userId)
    suspend fun getProject(id: String) = projectDao.get(id)

    suspend fun cachePayment(payment: PaymentEntity) = paymentDao.insert(payment)
    suspend fun listPayments(userId: String) = paymentDao.list(userId)
}

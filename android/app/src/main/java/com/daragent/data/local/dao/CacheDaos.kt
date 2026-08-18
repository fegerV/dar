package com.daragent.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.daragent.data.local.entity.EntitlementEntity
import com.daragent.data.local.entity.PaymentEntity
import com.daragent.data.local.entity.ProjectEntity
import com.daragent.data.local.entity.WalletEntity

@Dao
interface WalletDao {
    @Query("SELECT * FROM wallet WHERE user_id = :userId")
    suspend fun get(userId: String): WalletEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(wallet: WalletEntity)
}

@Dao
interface EntitlementDao {
    @Query("SELECT * FROM entitlements WHERE user_id = :userId")
    suspend fun list(userId: String): List<EntitlementEntity>

    @Query("SELECT * FROM entitlements WHERE id = :id")
    suspend fun get(id: String): EntitlementEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(entitlement: EntitlementEntity)
}

@Dao
interface ProjectDao {
    @Query("SELECT * FROM projects WHERE owner_user_id = :userId ORDER BY created_at DESC")
    suspend fun list(userId: String): List<ProjectEntity>

    @Query("SELECT * FROM projects WHERE id = :id")
    suspend fun get(id: String): ProjectEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(project: ProjectEntity)
}

@Dao
interface PaymentDao {
    @Query("SELECT * FROM payments WHERE user_id = :userId ORDER BY created_at DESC")
    suspend fun list(userId: String): List<PaymentEntity>

    @Query("SELECT * FROM payments WHERE id = :id")
    suspend fun get(id: String): PaymentEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(payment: PaymentEntity)
}

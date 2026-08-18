package com.daragent.data.local

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.daragent.data.local.dao.EntitlementDao
import com.daragent.data.local.dao.PaymentDao
import com.daragent.data.local.dao.ProjectDao
import com.daragent.data.local.dao.WalletDao
import com.daragent.data.local.entity.EntitlementEntity
import com.daragent.data.local.entity.PaymentEntity
import com.daragent.data.local.entity.ProjectEntity
import com.daragent.data.local.entity.WalletEntity

@Database(
    entities = [WalletEntity::class, EntitlementEntity::class, ProjectEntity::class, PaymentEntity::class],
    version = 1,
    exportSchema = false
)
abstract class DarAgentDatabase : RoomDatabase() {
    abstract fun walletDao(): WalletDao
    abstract fun entitlementDao(): EntitlementDao
    abstract fun projectDao(): ProjectDao
    abstract fun paymentDao(): PaymentDao

    companion object {
        @Volatile
        private var INSTANCE: DarAgentDatabase? = null

        fun getDatabase(context: Context): DarAgentDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    DarAgentDatabase::class.java,
                    "daragent.db"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}

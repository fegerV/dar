package com.daragent.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "wallet")
data class WalletEntity(
    @PrimaryKey val user_id: String,
    val balance_rub: Double,
    val bonus_balance: Double,
    val updated_at: String
)

@Entity(tableName = "entitlements")
data class EntitlementEntity(
    @PrimaryKey val id: String,
    val user_id: String,
    val code: String,
    val quantity: Int,
    val consumed: Int,
    val expires_at: String?,
    val source: String?,
    val created_at: String
)

@Entity(tableName = "projects")
data class ProjectEntity(
    @PrimaryKey val id: String,
    val owner_user_id: String,
    val recipient_id: String?,
    val title: String?,
    val status: String,
    val visibility: String,
    val occasion_code: String?,
    val occasion_title: String?,
    val selected_template_version_id: String?,
    val final_generation_id: String?,
    val price_rub: Double,
    val bonus_discount_rub: Double,
    val promo_discount_rub: Double,
    val paid_rub: Double,
    val created_at: String,
    val updated_at: String,
    val completed_at: String?,
    val cancelled_at: String?
)

@Entity(tableName = "payments")
data class PaymentEntity(
    @PrimaryKey val id: String,
    val user_id: String,
    val project_id: String?,
    val amount: Double,
    val status: String,
    val method: String,
    val external_payment_id: String?,
    val confirmation_url: String?,
    val created_at: String,
    val paid_at: String?
)

/*
  Warnings:

  - You are about to drop the column `uploadUrl` on the `File` table. All the data in the column will be lost.
  - You are about to drop the column `lemonSqueezyCustomerPortalUrl` on the `User` table. All the data in the column will be lost.
  - You are about to drop the `GptResponse` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "GptResponse" DROP CONSTRAINT "GptResponse_userId_fkey";

-- AlterTable
ALTER TABLE "File" DROP COLUMN "uploadUrl";

-- AlterTable
ALTER TABLE "User" DROP COLUMN "lemonSqueezyCustomerPortalUrl";

-- DropTable
DROP TABLE "GptResponse";
